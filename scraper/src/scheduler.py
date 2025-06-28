import schedule
import time
import asyncio
import psycopg2
import json
from datetime import datetime, timezone
from playwright.async_api import async_playwright
from bring_a_trailer import get_all_live

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
		browser = await p.chromium.launch(headless=True)
		data = await get_all_live(browser, debug=False)
		await browser.close()

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