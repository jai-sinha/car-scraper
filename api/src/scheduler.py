import schedule
import asyncio
import asyncpg
import time
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from playwright.async_api import async_playwright
import bring_a_trailer, pcarmarket, cars_and_bids

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	force=True
)
logging.getLogger("playwright").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

load_dotenv()

PG_CONN = {
	"host": os.environ.get("PG_HOST"),
	"database": os.environ.get("PG_DATABASE"),
	"user": os.environ.get("PG_USER"),
	"password": os.environ.get("PG_PASSWORD")
}

async def store_in_postgres(results: dict, context):
	conn = await asyncpg.connect(**PG_CONN)
	scraped_at = datetime.now(timezone.utc)

	try:
		# 1. Truncate and bulk-insert current scrape into temp_listings
		await conn.execute("TRUNCATE temp_listings")
		await conn.executemany("""
			INSERT INTO temp_listings (url, title, image, time, price, year, scraped_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
		""", [
			(listing["url"], listing["title"], listing["image"], 
				listing["time"], listing["price"], listing["year"], scraped_at)
			for listing in results.values()
		])

		# 2. Find new listings (in temp, not in live)
		new_urls = [row[0] for row in await conn.fetch("""
			SELECT t.url FROM temp_listings t
			LEFT JOIN live_listings l ON t.url = l.url
			WHERE l.url IS NULL
		""")]

		# 3. Find closed listings (in live, not in temp)
		closed_rows = await conn.fetch("""
			SELECT l.url, l.title, l.image, l.time, l.price, l.year, l.scraped_at
			FROM live_listings l
			LEFT JOIN temp_listings t ON l.url = t.url
			WHERE t.url IS NULL
		""")
		
		# Bulk insert closed listings and bulk delete from live
		if closed_rows:
			await conn.executemany("""
				INSERT INTO closed_listings (url, title, image, price, year, closed_at)
				VALUES ($1, $2, $3, $4, $5, $6)
				ON CONFLICT (url) DO NOTHING
			""", [
				(row[0], row[1], row[2], row[4], row[5], scraped_at)
				for row in closed_rows
			])
			
			await conn.executemany("""
				DELETE FROM live_listings WHERE url = $1
			""", [(row[0],) for row in closed_rows])

		# 4. Update existing listings (in both temp and live)
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
				(row[0], row[1], row[2], scraped_at)  # Use the current scraped_at
				for row in update_rows
			])

		# 5. Insert new listings (in temp, not in live)
		new_listings = [next(l for l in results.values() if l["url"] == url) for url in new_urls]
		
		# Bulk insert new listings
		if new_listings:
			await conn.executemany("""
				INSERT INTO live_listings (url, title, image, time, price, year, scraped_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7)
			""", [
				(listing["url"], listing["title"], listing["image"],
				listing["time"], listing["price"], listing["year"], scraped_at)
				for listing in new_listings
			])

		# 6. Check for live_listings that need keyword scraping
		no_keywords = await conn.fetch("""
			SELECT url, title, image, time, price, year, scraped_at, keywords
			FROM live_listings
			WHERE keywords IS NULL OR keywords = ''
			LIMIT 100;
		""")
		
		if no_keywords:
			# Convert to dicts for downstream compatibility
			listings_to_scrape = [
				{
					"url": row["url"],
					"title": row["title"],
					"image": row["image"],
					"time": row["time"],
					"price": row["price"],
					"year": row["year"],
					"scraped_at": row["scraped_at"],
					"keywords": row["keywords"] if row["keywords"] else []
				}
				for row in no_keywords
			]

			# Run keyword scrapers for each listing synchronously, due to resource constraints
			for listing in listings_to_scrape:
				if not listing.get("keywords"):
					if listing['title'].startswith("BaT: "):
						await bring_a_trailer.get_listing_details(listing, context)
					elif listing['title'].startswith("PCAR:"):
						await pcarmarket.get_listing_details(listing, context)
					elif listing['title'].startswith("C&B: "):
						await cars_and_bids.get_listing_details(listing, context)

			# Update database with scraped keywords
			updates = []
			for listing in listings_to_scrape:
				if listing.get("keywords"):
					logging.info(f"Updating keywords for {listing['title']}")
					updates.append((listing["url"], listing["keywords"]))

			if updates:
				await conn.executemany("""
					UPDATE live_listings 
					SET keywords = to_tsvector('english', $2) 
					WHERE url = $1
				""", updates)
				
				logging.info(f"Updated keywords for {len(updates)} listings")

	except Exception as e:
		logging.error(f"Error storing data in Postgres: {e}")
		raise
	finally:
		await conn.close()

async def run_scrapers():
	async with async_playwright() as p:
		# Create browser, contexts for each scraper
		browser = await p.chromium.launch(headless=True,
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
		context_cab = await browser.new_context(
			user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			viewport={'width': 800, 'height': 600},
			locale='en-US',
			timezone_id='America/New_York'
		)
		context_bat = await browser.new_context(viewport={"width": 800, "height": 600})
		context_pcar = await browser.new_context(viewport={"width": 800, "height": 600})
		for ctx in [context_bat, context_pcar, context_cab]:
			await ctx.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "media", "font"] else route.continue_())
		try:
			results = await asyncio.gather(
				bring_a_trailer.get_all_live(context_bat),
				pcarmarket.get_all_live(context_pcar),
				cars_and_bids.get_all_live(context_cab)
			)
			for i, name in enumerate(['bat', 'pcar', 'cab']):
				logging.info(f"{name} returned {len(results[i])} listings")
				if (name == 'bat' and len(results[i]) < 500) or len(results[i]) == 0:
					# Skip upload to prevent incomplete data messing with the database
					logging.warning(f"Incomplete results for {name}. Skipping upload.")
					return
					
			# Combine results
			data = {}
			for result_dict in results:
				data.update(result_dict)
				
			await store_in_postgres(data, context_cab)

		except Exception as e:
			logging.error(f"Error during scraping: {e}")
			raise

		finally:
			for ctx in [context_bat, context_pcar, context_cab]:
				await ctx.close()

			await browser.close()

def job():
	logging.info("Job started")
	try:
		asyncio.run(run_scrapers())
	except Exception as e:
		logging.error(f"Job failed: {e}")
	logging.info("Job finished")

if __name__ == "__main__":
	schedule.every(2).minutes.do(job)
	job()  # run once on startup
	while True:
		schedule.run_pending()
		time.sleep(60)