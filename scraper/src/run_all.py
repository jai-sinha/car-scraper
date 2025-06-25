import asyncio
from playwright.async_api import async_playwright
import cars_and_bids, pcarmarket, bring_a_trailer

async def run_scrapers(query):
	"""Run all scrapers asynchronously and return combined results"""
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
		
		context = await browser.new_context(
			user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			viewport={'width': 1920, 'height': 1080},
			locale='en-US',
			timezone_id='America/New_York'
		)
		
		try:
			results = await asyncio.gather(
				bring_a_trailer.get_results(query, context),
				pcarmarket.get_results(query, context),
				cars_and_bids.get_results(query, context)
			)
		finally:
			await browser.close()
		
		# Combine results
		combined = {}
		for result_dict in results:
			combined.update(result_dict)
		
		return combined

if __name__ == "__main__":
	async def test():
		from urllib.parse import quote
		query = quote("Porsche 911 991")
		results = await run_scrapers(query)
		print(results)

	asyncio.run(test())
