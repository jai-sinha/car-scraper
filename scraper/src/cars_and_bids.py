from playwright.async_api import async_playwright
from urllib.parse import quote
import asyncio
import listing

TIMEOUT = 10000

async def get_results(car: listing.Car, browser, debug=False):
	"""
	Fetches search results from Cars & Bids for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""

	# Encode car info for url
	q = car.encode()
	q = "%20".join(q)
	search_url = "https://carsandbids.com/search?q=" + q
	if debug:
		print(search_url)

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		await page.wait_for_function(
			"""() => {
					return document.querySelector('ul.auctions-list') !== null ||
							document.body.textContent.includes('No live auctions');
			}""",
			timeout=TIMEOUT
		)
		
		# If there were no results, simply return an empty dict
		if not await page.query_selector('ul.auctions-list'):
			if debug:
				print("No listings found")
			return {}

		listings_data = await page.evaluate("""
			() => {
				const items = document.querySelectorAll('ul.auctions-list li.auction-item');
				return Array.from(items).map(item => ({
					title: item.querySelector('a.hero')?.getAttribute('title') || '',
					url: item.querySelector('a.hero')?.getAttribute('href') || '',
					bid: item.querySelector('.bid-value')?.textContent?.trim() || '',
					timeRemaining: item.querySelector('.time-left .value')?.textContent?.trim() || '',
					image: item.querySelector('img')?.getAttribute('src') || ''
				}));
			}
		""")
		
		# Process each listing
		# All live listings and the 30 most recent closed ones will be visible,
		# so remove the closed ones from the count/processing
		if debug:
			print(f"Found {len(listings_data) - 30} auction listings")

		out = {}
		for data in listings_data:
			if not data['title'] or not data['timeRemaining']:
				continue
			
			# Create listing
			key = f"C&B: {data['title']}"
			url = f"https://carsandbids.com{data['url']}"
			out[key] = listing.Listing(key, url, data['image'], data['timeRemaining'], data['bid'])

			if debug:			
				print(f"Title: {data['title']}")
				print(f"URL: {url}")
				print(f"Image URL: {data['image']}")
				print(f"Current Bid: {data['bid']}")
				print(f"Time Remaining: {data['timeRemaining']}")
				print("-" * 50)

		# Return dict of C&B results
		return out

	except Exception as e:
		print(f"Error scraping C&B auctions: {e}")
		return {}


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
			context = await browser.new_context(
				user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
				viewport={'width': 1920, 'height': 1080},
				locale='en-US',
				timezone_id='America/New_York'
			)

			try:
				car = listing.Car("Mercedes", "356")
				result = await get_results(car, context, debug=True)

			finally:
				await browser.close()
	
	asyncio.run(test())
