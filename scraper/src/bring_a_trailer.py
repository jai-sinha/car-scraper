from playwright.async_api import async_playwright
import asyncio
import listing

TIMEOUT = 10000

async def get_results(query, browser, debug=False):
	"""
	Fetches search results from bring a trailer for a given car, extracts listing details, and stores them in a dictionary.

	Args:
		car: The desired car to search.
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""

	# Encode car info for url, BaT uses "+" instead of "%20"
	query = query.replace("%20", "+")
	search_url = "https://bringatrailer.com/auctions/?search=" + query
	if debug:
		print(search_url)
	

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		
		# Check filter input value to confirm search filtering has occurred
		search_terms = f"{query.replace('+', ' ')}"
		await page.wait_for_function(
			f'''
			document.querySelector("input[data-bind=\\"textInput: filterTerm\\"]").value.includes("{search_terms}")
			''',
			timeout=TIMEOUT
		)

		# Then confirm there are live auctions matching the filter
		await page.wait_for_function(
			"""() => {
					return document.querySelector('.listing-card') ||
							document.querySelector('#auctions_filtered_message_none');
			}""",
			timeout=TIMEOUT
		)
		
		# If there were no results, simply return an empty dict
		if not await page.query_selector('.listing-card'):
			if debug:
				print("No listings found")
			return {}

		listings_data = await page.evaluate("""
			() => {
				const items = document.querySelectorAll('.listing-card');
				return Array.from(items).map(item => ({
					title: item.querySelector('h3')?.textContent?.trim() || '',
					url: item.href || '',
					image: item.querySelector('.thumbnail img')?.src || '',
					bid: item.querySelector('.bidding-bid .bid-formatted')?.textContent?.trim() || '',
					timeRemaining: item.querySelector('.countdown-text')?.textContent?.trim() || ''
				}));
			}
		""")

		# Process each listing
		if debug:
			print(f"Found {len(listings_data)} listings")

		out = {}
		for data in listings_data:
			if not data['title'] or not data['url']:
				continue
				
			# Clean up bid text
			bid = data['bid']
			if bid.startswith("USD "):
				bid = bid[4:]

			# Format time, removing seconds
			timeRemaining = data['timeRemaining']
			if ":" in timeRemaining:
				if timeRemaining.count(":") > 1:
					timeRemaining = f"{timeRemaining[:2]}h {timeRemaining[3:5]}m"
				else:
					timeRemaining = f"{timeRemaining[:2]}m"
			elif "days" not in timeRemaining:
				timeRemaining = "0m"
			
			# Create listing
			key = "BaT: " + data['title']
			out[key] = listing.Listing(key, data['url'], data['image'], timeRemaining, bid)
			
			if debug:
				print(f"Title: {data['title']}")
				print(f"URL: {data['url']}")
				print(f"Image: {data['image']}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {timeRemaining}")
				print("-" * 50)

		# Return dict of BaT results
		return out				

	except Exception as e:
		print(f'Error fetching BaT results: {e}')
		return {}


if __name__ == "__main__":
	async def test():
		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)

			try:
				from urllib.parse import quote
				query = quote("911 991")
				await get_results(query, browser, debug=True)

			finally:
				await browser.close()
	
	asyncio.run(test())
	