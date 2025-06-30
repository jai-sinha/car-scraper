import schedule
import time
import asyncio
import psycopg2
from datetime import datetime, timezone
from playwright.async_api import async_playwright
import bring_a_trailer, pcarmarket, cars_and_bids

PG_CONN = {
	"host": "postgres",
	"database": "live_auctions",
	"user": "username",
	"password": "password"
}

def store_in_postgres(results):
	conn = psycopg2.connect(**PG_CONN)
	cur = conn.cursor()
	scraped_at = datetime.now(timezone.utc)
	cur.execute("DELETE FROM listings;") # Clear previous listings
	for key, listing in results.items():
		cur.execute("""
			INSERT INTO listings (source, title, url, image, time, price, year, scraped_at)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
		""", (
			"bringatrailer",  # or dynamic source
			listing["title"],
			listing["url"],
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
		# bringatrailer
		browser_bat = await p.chromium.launch(headless=True)
		context_bat = await browser_bat.new_context()
		# pcarmarket
		browser_pcar = await p.chromium.launch(headless=True)
		context_pcar = await browser_pcar.new_context()
		# carsandbids with custom context and args
		browser_cab = await p.chromium.launch(headless=True,
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
		context_cab = await browser_cab.new_context(
			user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			viewport={'width': 1920, 'height': 1080},
			locale='en-US',
			timezone_id='America/New_York'
		)
		try:
			results = await asyncio.gather(
				bring_a_trailer.get_all_live(context_bat),
				pcarmarket.get_all_live(context_pcar),
				cars_and_bids.get_all_live(context_cab)
			)
		finally:
			await browser_bat.close()
			await browser_pcar.close()
			await browser_cab.close()
		# Combine results
		data = {}
		for result_dict in results:
			data.update(result_dict)

	store_in_postgres(data)

def job():
	asyncio.run(run_scrapers())

if __name__ == "__main__":
	schedule.every(30).minutes.do(job)
	time.sleep(360)
	job()  # run once on startup
	while True:
		schedule.run_pending()
		time.sleep(60)