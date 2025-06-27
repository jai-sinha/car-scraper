import schedule
import time
import asyncio
import redis
import json
from datetime import datetime
from playwright.async_api import async_playwright
from bring_a_trailer import get_all_live

REDIS_HOST = "redis"  # docker-compose service name

def store_in_redis(results):
	r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
	r.set(f"bat_listings", json.dumps(results))

async def run_scraper():
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		data = await get_all_live(browser, debug=False)
		await browser.close()
	store_in_redis(data)
	print(f"Scrape complete at: {datetime.now()}")

def job():
	asyncio.run(run_scraper())

if __name__ == "__main__":
	schedule.every(30).minutes.do(job)
	job()  # run once on startup
	while True:
		schedule.run_pending()
		time.sleep(60)