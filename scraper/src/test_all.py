import asyncio
from playwright.async_api import async_playwright
import listing, cars_and_bids, pcarmarket, bring_a_trailer
from flask import Flask, request, jsonify
from flask_cors import CORS

if __name__ == "__main__":
	async def test():
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
			browser = await browser.new_context(
				user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
				viewport={'width': 1920, 'height': 1080},
				locale='en-US',
				timezone_id='America/New_York'
			)

			try:
				car = listing.Car("Porsche", "911", "991")
				results = await asyncio.gather(
					bring_a_trailer.get_results(car, browser),
					pcarmarket.get_results(car, browser),
					cars_and_bids.get_results(car, browser)
				)

			finally:
				await browser.close() 

			combined = {}
			for result_dict in results:
				combined.update(result_dict)

			print(combined)

	asyncio.run(test())
