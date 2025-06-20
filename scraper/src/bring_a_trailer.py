from playwright.async_api import async_playwright
from urllib.parse import quote
import asyncio
import listing

TIMEOUT = 10000

async def get_results(car: listing.Car, browser, debug=False):
	"""
	Fetches search results from bring a trailer for a given car, extracts listing details, and stores them in a dictionary.

	Args:
		car: The desired car to search.
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""

	# Encode car info for url
	q = quote(car.make), quote(car.generation), quote(car.model)
	q = "+".join(q)
	search_url = "https://bringatrailer.com/auctions/?search=" + q
	if debug:
		print(search_url)
	

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		
		# Check filter input value to confirm search filtering has occurred
		search_terms = f"{car.make} {car.generation} {car.model}"
		await page.wait_for_function(
			f'''
			document.querySelector("input[data-bind=\\"textInput: filterTerm\\"]").value.includes("{search_terms}")
			''',
			timeout=6000
		)

		await page.wait_for_selector('.listing-card', timeout=TIMEOUT)

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

			# Clean up time, removing seconds
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
				car = listing.Car("Porsche", "911", "991")
				result = await get_results(car, browser, debug=True)

			finally:
				await browser.close()
	
	asyncio.run(test())
	