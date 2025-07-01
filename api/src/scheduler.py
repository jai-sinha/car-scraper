import schedule
import asyncio
import psycopg2
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

load_dotenv()

PG_CONN = {
	"host": os.environ.get("PG_HOST"),
	"database": os.environ.get("PG_DATABASE"),
	"user": os.environ.get("PG_USER"),
	"password": os.environ.get("PG_PASSWORD")
}

def store_in_postgres(results: dict):
	conn = psycopg2.connect(**PG_CONN)
	cur = conn.cursor()
	scraped_at = datetime.now(timezone.utc)

	# 1. Truncate and bulk-insert current scrape into temp_listings
	cur.execute("TRUNCATE temp_listings")
	for listing in results.values():
		cur.execute("""
			INSERT INTO temp_listings (url, title, image, time, price, year, scraped_at)
			VALUES (%s, %s, %s, %s, %s, %s, %s)
		""", (
			listing["url"],
			listing["title"],
			listing["image"],
			listing["time"],
			listing["price"],
			listing["year"],
			scraped_at
		))

	# 2. Find new listings (in temp, not in live)
	cur.execute("""
		SELECT t.url FROM temp_listings t
		LEFT JOIN live_listings l ON t.url = l.url
		WHERE l.url IS NULL
	""")
	new_urls = [row[0] for row in cur.fetchall()]

	# 3. Find closed listings (in live, not in temp)
	cur.execute("""
		SELECT l.url, l.title, l.image, l.time, l.price, l.year, l.scraped_at
		FROM live_listings l
		LEFT JOIN temp_listings t ON l.url = t.url
		WHERE t.url IS NULL
	""")
	closed_rows = cur.fetchall()
	for row in closed_rows:
		url, title, image, _, price, year, _ = row
		cur.execute("""
			INSERT INTO closed_listings (url, title, image, price, year, closed_at)
			VALUES (%s, %s, %s, %s, %s, %s)
			ON CONFLICT (url) DO NOTHING
		""", (url, title, image, price, year, scraped_at))
		cur.execute("DELETE FROM live_listings WHERE url = %s", (row[0],))

	# 4. Update existing listings (in both temp and live)
	cur.execute("""
		SELECT t.url, t.time, t.price, t.scraped_at
		FROM temp_listings t
		INNER JOIN live_listings l ON t.url = l.url
	""")
	for url, time_val, price, scraped in cur.fetchall():
		cur.execute("""
			UPDATE live_listings
			SET time = %s, price = %s, scraped_at = %s
			WHERE url = %s
		""", (time_val, price, scraped, url))

	# 5. Insert new listings (in temp, not in live)
	for url in new_urls:
		listing = next(l for l in results.values() if l["url"] == url)
		# Optionally crawl for keywords here
		cur.execute("""
			INSERT INTO live_listings (url, title, image, time, price, year, scraped_at)
			VALUES (%s, %s, %s, %s, %s, %s, %s)
		""", (
			listing["url"],
			listing["title"],
			listing["image"],
			listing["time"],
			listing["price"],
			listing["year"],
			scraped_at
		))

	conn.commit()
	cur.close()
	conn.close()

async def run_scrapers():
	async with async_playwright() as p:
		# carsandbids with custom context and args
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
			viewport={'width': 1920, 'height': 1080},
			locale='en-US',
			timezone_id='America/New_York'
		)
		# bringatrailer, pcarmarket
		context_bat = await browser.new_context()
		context_pcar = await browser.new_context()
		try:
			results = await asyncio.gather(
				bring_a_trailer.get_all_live(context_bat),
				pcarmarket.get_all_live(context_pcar),
				cars_and_bids.get_all_live(context_cab)
			)
			for i, name in enumerate(['bat', 'pcar', 'cab']):
				print(f"{name} returned {len(results[i])} listings")
					
		finally:
			await browser.close()

		# Combine results
		data = {}
		for result_dict in results:
			data.update(result_dict)

	store_in_postgres(data)

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