import schedule
import asyncio
import asyncpg
import time
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from playwright.async_api import async_playwright, BrowserContext
from typing import Dict, Tuple
import bring_a_trailer, pcarmarket, cars_and_bids

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	force=True
)
logging.getLogger("playwright").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Database configuration
PG_CONN = {
	"host": os.environ.get("PG_HOST"),
	"database": os.environ.get("PG_DATABASE"),
	"user": os.environ.get("PG_USER"),
	"password": os.environ.get("PG_PASSWORD")
}

# Constants
MIN_BAT_LISTINGS = 500
KEYWORD_BATCH_SIZE = 25
SCHEDULE_INTERVAL_MINUTES = 2


class ScraperScheduler:
	"""Main scheduler class for coordinating scraping operations."""
	
	def __init__(self):
		self.scrapers = {
			'bat': bring_a_trailer,
			'pcar': pcarmarket,
			'cab': cars_and_bids
		}
	
	async def create_browser_contexts(self, browser) -> Tuple[BrowserContext, BrowserContext, BrowserContext]:
		"""Create browser contexts for each scraper with appropriate settings."""
		# Cars & Bids context with full user agent
		context_cab = await browser.new_context(
			user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			viewport={'width': 800, 'height': 600},
			locale='en-US',
			timezone_id='America/New_York'
		)
		
		# Standard contexts for other scrapers
		context_bat = await browser.new_context(viewport={"width": 800, "height": 600})
		context_pcar = await browser.new_context(viewport={"width": 800, "height": 600})
		
		# Block resources to speed up scraping
		contexts = [context_bat, context_pcar, context_cab]
		for ctx in contexts:
			await ctx.route(
				"**/*", 
				lambda route, request: route.abort() 
				if request.resource_type in ["image", "media", "font"] 
				else route.continue_()
			)
		
		return context_bat, context_pcar, context_cab
	
	async def run_all_scrapers(self) -> Dict:
		"""Run all scrapers concurrently and return combined results."""
		async with async_playwright() as p:
			browser = await p.chromium.launch(
				headless=True,
				args=[
					'--no-sandbox',
					'--disable-setuid-sandbox',
					'--disable-dev-shm-usage',
					'--disable-accelerated-2d-canvas',
					'--no-first-run',
					'--no-zygote',
					'--disable-gpu',
					'--disable-web-security',
					'--disable-features=VizDisplayCompositor'
				]
			)
			
			context_bat, context_pcar, context_cab = await self.create_browser_contexts(browser)
			
			try:
				# Run all scrapers concurrently
				results = await asyncio.gather(
					bring_a_trailer.get_all_live(context_bat),
					pcarmarket.get_all_live(context_pcar),
					cars_and_bids.get_all_live(context_cab)
				)
				
				# Validate results
				scraper_names = ['bat', 'pcar', 'cab']
				for i, name in enumerate(scraper_names):
					listing_count = len(results[i])
					logging.info(f"{name} returned {listing_count} listings")
					
					if self._should_skip_upload(name, listing_count):
						logging.warning(f"Incomplete results for {name}. Skipping upload.")
						return {}
				
				# Combine and return results
				combined_data = {}
				for result_dict in results:
					combined_data.update(result_dict)
				
				# Process keywords for new listings
				await self._process_keywords(context_cab)
				
				return combined_data
					
			finally:
				for ctx in [context_bat, context_pcar, context_cab]:
					await ctx.close()
				await browser.close()
	
	def _should_skip_upload(self, scraper_name: str, listing_count: int) -> bool:
		"""Determine if we should skip uploading based on listing count."""
		if listing_count == 0:
			return True
		if scraper_name == 'bat' and listing_count < MIN_BAT_LISTINGS:
			return True
		return False
	
	async def _process_keywords(self, context: BrowserContext) -> None:
		"""Process keyword extraction for listings that need it."""
		conn = await asyncpg.connect(**PG_CONN)
		try:
			# Get listings that need keyword extraction
			no_keywords = await conn.fetch("""
				SELECT url, title, image, time, price, year, scraped_at, keywords
				FROM live_listings
				WHERE keywords IS NULL OR keywords = ''
				LIMIT $1;
			""", KEYWORD_BATCH_SIZE)
			
			if not no_keywords:
				return
			
			# Extract keywords for each listing
			updates = []
			for listing in no_keywords:
				kw = await self._extract_keywords_for_listing(listing, context)
				if kw:
					updates.append((listing["url"], kw))
			
			# Update database with new keywords
			if updates:
				await conn.executemany("""
					UPDATE live_listings 
					SET keywords = to_tsvector('english', $2) 
					WHERE url = $1
				""", updates)
				logging.info(f"Updated keywords for {len(updates)} listings")
					
		finally:
			await conn.close()
	
	async def _extract_keywords_for_listing(self, listing: asyncpg.Record, context: BrowserContext) -> None:
		"""Extract keywords for a single listing based on its source."""
		title = listing['title']

		try:
			if title.startswith("BaT"):
				kw = await bring_a_trailer.get_listing_details(listing["title"], listing["url"] , context)
			elif title.startswith("PCAR"):
				kw = await pcarmarket.get_listing_details(listing["title"], listing["url"], context)
			elif title.startswith("C&B"):
				kw = await cars_and_bids.get_listing_details(listing["title"], listing["url"], context)

			if kw:
				logging.info(f"Extracted keywords for {title}")
				return kw
					
		except Exception as e:
			logging.error(f"Error extracting keywords for {title}: {e}")


class DatabaseManager:
	"""Handles all database operations for the scraper."""
	
	@staticmethod
	async def store_listings(results: Dict) -> None:
		"""Store scraping results in PostgreSQL database."""
		conn = await asyncpg.connect(**PG_CONN)
		scraped_at = datetime.now(timezone.utc)
		
		try:
			# Step 1: Refresh temp table with current scrape
			await DatabaseManager._refresh_temp_table(conn, results, scraped_at)
			
			# Step 2: Handle closed listings
			await DatabaseManager._process_closed_listings(conn, scraped_at)
			
			# Step 3: Update existing listings
			await DatabaseManager._update_existing_listings(conn, scraped_at)
			
			# Step 4: Insert new listings
			await DatabaseManager._insert_new_listings(conn, results, scraped_at)
			
		except Exception as e:
			logging.error(f"Error storing data in Postgres: {e}")
			raise
		finally:
			await conn.close()
	
	@staticmethod
	async def _refresh_temp_table(conn, results: Dict, scraped_at: datetime) -> None:
		"""Truncate and repopulate temp_listings table."""
		await conn.execute("TRUNCATE temp_listings")
		
		if results:
			await conn.executemany("""
				INSERT INTO temp_listings (url, title, image, time, price, year, scraped_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7)
			""", [
				(listing["url"], listing["title"], listing["image"], 
				listing["time"], listing["price"], listing["year"], scraped_at)
				for listing in results.values()
			])
	
	@staticmethod
	async def _process_closed_listings(conn, scraped_at: datetime) -> None:
		"""Move closed listings from live to closed table."""
		closed_rows = await conn.fetch("""
			SELECT l.url, l.title, l.image, l.time, l.price, l.year, l.scraped_at
			FROM live_listings l
			LEFT JOIN temp_listings t ON l.url = t.url
			WHERE t.url IS NULL
		""")
		
		if closed_rows:
			# Insert into closed_listings
			await conn.executemany("""
				INSERT INTO closed_listings (url, title, image, price, year, closed_at)
				VALUES ($1, $2, $3, $4, $5, $6)
				ON CONFLICT (url) DO NOTHING
			""", [
				(row[0], row[1], row[2], row[4], row[5], scraped_at)
				for row in closed_rows
			])
			
			# Remove from live_listings
			await conn.executemany("""
				DELETE FROM live_listings WHERE url = $1
			""", [(row[0],) for row in closed_rows])
			
			logging.info(f"Moved {len(closed_rows)} closed listings")
	
	@staticmethod
	async def _update_existing_listings(conn, scraped_at: datetime) -> None:
		"""Update existing listings with new data."""
		update_rows = await conn.fetch("""
			SELECT t.url, t.time, t.price, t.scraped_at
			FROM temp_listings t
			INNER JOIN live_listings l ON t.url = l.url
		""")
		
		if update_rows:
			await conn.executemany("""
				UPDATE live_listings
				SET time = $2, price = $3, scraped_at = $4
				WHERE url = $1
			""", [
				(row[0], row[1], row[2], scraped_at)
				for row in update_rows
			])
			
			logging.info(f"Updated {len(update_rows)} existing listings")
	
	@staticmethod
	async def _insert_new_listings(conn, results: Dict, scraped_at: datetime) -> None:
		"""Insert new listings into live_listings table."""
		new_urls = [row[0] for row in await conn.fetch("""
			SELECT t.url FROM temp_listings t
			LEFT JOIN live_listings l ON t.url = l.url
			WHERE l.url IS NULL
		""")]
		
		if new_urls:
			new_listings = [
				next(l for l in results.values() if l["url"] == url) 
				for url in new_urls
			]
			
			await conn.executemany("""
				INSERT INTO live_listings (url, title, image, time, price, year, scraped_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7)
			""", [
				(listing["url"], listing["title"], listing["image"],
				listing["time"], listing["price"], listing["year"], scraped_at)
				for listing in new_listings
			])
			
			logging.info(f"Inserted {len(new_listings)} new listings")


async def run_scrapers():
	"""Main function to run all scrapers and store results."""
	scheduler = ScraperScheduler()
	
	try:
		# Run scrapers and get results
		results = await scheduler.run_all_scrapers()
		
		if results:  # Only store if we have valid results
			await DatabaseManager.store_listings(results)
			logging.info(f"Successfully processed {len(results)} total listings")
		else:
			logging.warning("No results to store")
			
	except Exception as e:
		logging.error(f"Error during scraping: {e}")
		raise


def job():
	"""Wrapper function for scheduled job execution."""
	logging.info("Scheduled job started")
	try:
		asyncio.run(run_scrapers())
	except Exception as e:
		logging.error(f"Job failed: {e}")
	logging.info("Scheduled job finished")


if __name__ == "__main__":
	schedule.every(SCHEDULE_INTERVAL_MINUTES).minutes.do(job)
	job()  # Run once on startup
	
	while True:
		schedule.run_pending()
		time.sleep(60)