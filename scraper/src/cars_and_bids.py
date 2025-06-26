from playwright.async_api import async_playwright
import re
import asyncio
import listing

TIMEOUT = 10000

async def get_results(query, browser, debug=False):
	"""
	Fetches search results from Cars & Bids for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		query: The desired car to search, formatted as a URL-encoded string.
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""

	search_url = "https://carsandbids.com/search?q=" + query
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

			# Extract year from title using regex
			year_match = re.search(r'\b(19|20)\d{2}\b', data['title'])
			year = int(year_match.group(0)) if year_match else None
		
			# Format, removing seconds, and lowercasing "Day" if present
			timeRemaining = str(data['timeRemaining']).lower()
			if "day" in timeRemaining: # Keep days as-is (e.g., "1 day", "2 days")
				pass
			elif ":" in timeRemaining: # Handle time formats like "1:23:45" or "23:45"
				parts = timeRemaining.split(":")
				if len(parts) == 3:  # hours:minutes:seconds
					timeRemaining = f"{parts[0]}h {parts[1]}m"
				elif len(parts) == 2 and int(parts[0]) > 0:  # minutes:seconds (and minutes > 0)
					timeRemaining = f"{parts[0]}m"
			else: # No colons and no days means just seconds remaining
				timeRemaining = "0m"
			
			# Create listing
			key = f"C&B: {data['title']}"
			url = f"https://carsandbids.com{data['url']}"
			out[key] = listing.Listing(key, url, data['image'], timeRemaining, data['bid'], year)

			if debug:			
				print(f"Title: {data['title']}")
				print(f"URL: {url}")
				print(f"Year: {year}")
				print(f"Current Bid: {data['bid']}")
				print(f"Time Remaining: {timeRemaining}")
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
				from urllib.parse import quote
				query = quote("997 911")
				await get_results(query, context, debug=True)

			finally:
				await browser.close()
	
	asyncio.run(test())
