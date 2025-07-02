from playwright.async_api import async_playwright
import re
import asyncio
import listing
from datetime import timezone, datetime, timedelta

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
	
async def get_all_live(browser, debug=False):
	"""
	Fetches all live auctions from Cars & Bids, and returns them as a dict.

	Args:
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""
	search_url = "https://carsandbids.com"
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

		# Slowly scroll to fight lazy loading
		await page.evaluate("""
			() => {
				return new Promise(resolve => {
					let count = 0;
					const scrollStep = window.innerHeight;
					function scrollAndCheck() {
						window.scrollBy(0, scrollStep);
						setTimeout(() => {
							const items = document.querySelectorAll('ul.auctions-list li.auction-item').length;
							if (count < 20) { // Scroll 20 times, 4 page heights per second
								count++;
								scrollAndCheck();
							} else {
								resolve();
							}
						}, 250); // 4 page heights per second
					}
					scrollAndCheck();
				});
			}
		""")

		listings_data = await page.evaluate("""
			() => {
				const items = document.querySelectorAll('ul.auctions-list li.auction-item');
				return Array.from(items)
					.map(item => {
						const a = item.querySelector('.auction-title a');
						const title = a?.getAttribute('title') || '';
						const url = a?.getAttribute('href') || '';
						const bid = item.querySelector('.high-bid .bid-value')?.textContent?.trim() || '';
						const timeRemaining = item.querySelector('.time-left .value span')?.textContent?.trim() || '';
						const image = item.querySelector('img')?.getAttribute('src') || '';
						return { title, url, bid, timeRemaining, image };
					})
					.filter(item => item.title && item.url);
			}
		""")
		
		# Process each listing
		if debug:
			print(f"Found {len(listings_data)} auction listings")

		scrape_time = datetime.now(timezone.utc)
		out = {}
		for data in listings_data:
			if not data['title'] or not data['timeRemaining']:
				continue

			# Extract year from title using regex
			year_match = re.search(r'\b(19|20)\d{2}\b', data['title'])
			year = int(year_match.group(0)) if year_match else None
		
			# Process end time in UTC
			timeRemaining = str(data['timeRemaining']).lower()
			if "day" in timeRemaining.lower(): # Keep days as-is (e.g., "1 day", "2 days")
				delta = timedelta(days=int(timeRemaining.split()[0]))
			elif ":" in timeRemaining: # Handle time formats like "1:23:45" or "23:45"
				parts = timeRemaining.split(":")
				if len(parts) == 3:  # hours:minutes:seconds
					delta = timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=int(parts[2]))
				elif len(parts) == 2:  # minutes:seconds
					delta = timedelta(minutes=int(parts[0]), seconds=int(parts[1]))
			elif "ended" in timeRemaining.lower():
				delta = timedelta(seconds=2)  # Give a small buffer for ended auctions
			else: # No colons and no days means just seconds remaining
				delta = timedelta(seconds=int(timeRemaining.split('s')[0]))

			end_time = scrape_time + delta
			
			# Create listing
			url = f"https://carsandbids.com{data['url']}"
			out[url] = listing.Listing(f"C&B: {data['title']}", url, data['image'], end_time, data['bid'], year).to_dict()

			if debug:
				print(f"Title: {data['title']}")
				print(f"URL: {url}")
				print(f"Year: {year}")
				print(f"Current Bid: {data['bid']}")
				print(f"End Time (UTC): {end_time.isoformat()}")
				print("-" * 50)

		# Return dict of C&B results
		return out

	except Exception as e:
		print(f"Error scraping C&B auctions: {e}")
		return {}
	
	finally:
		await page.close()

async def get_listing_details(listing: dict, context, debug=False):
	"""
	Fetches details and keywords for a specific listing from Cars & Bids. Async even though it doesn't need to be, for the sake of consistency.

	Args:
		listing: The Listing dict to fetch details for
		context: Playwright async browser context
		debug: Print all info
	Returns:
		None, modifies the listing object in place
	"""
	page = await context.new_page()
	try:
		await page.goto(listing["url"], timeout=TIMEOUT)
		
		await page.wait_for_selector('.quick-facts', timeout=TIMEOUT)

		listing_keywords = await page.evaluate("""
			() => {
				const facts = {};
				const dts = Array.from(document.querySelectorAll('.quick-facts dt'));
				dts.forEach(dt => {
						const key = dt.textContent.trim();
						const dd = dt.nextElementSibling;
						let value = '';
						if (dd) {
							const a = dd.querySelector('a');
							value = a ? a.textContent.trim() : dd.textContent.trim();
						}
						facts[key] = value;
				});
				return {
						make: facts['Make'] || null,
						model: facts['Model'] || null
				};
			}
		""")

		if "keywords" not in listing:
			listing["keywords"] = []
		listing["keywords"].extend([listing_keywords.get("make", ""), listing_keywords.get("model", "")])
		listing["keywords"].append(listing["title"])

		if debug:
			print(f"Keywords for {listing['title']}: {listing['keywords']}")

	except Exception as e:
		print(f'Error fetching C&B details for {listing["title"]}: {e}')

	finally:
		await page.close()


if __name__ == "__main__":
	async def test(test_type):
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
			
			match test_type:
				case "results":
					try:
						from urllib.parse import quote
						query = quote("997 911")
						results = await get_results(query, context, debug=True)
						print(results)

					finally:
						await browser.close()

				case "live":
					try:
						res = await get_all_live(context, debug=True)
						print(res)

					finally:
						await browser.close()

				case "keywords":
					try:
						url = "https://carsandbids.com/auctions/rx4XwZR0/2012-bmw-m3-coupe-competition-package?ss_id=74c51f8b-8c62-4b4a-a504-560438e4c87b&ref=lr_1_1"
						test_listing = listing.Listing("blah blah", url, "", "", "", 0)
						await get_listing_details(test_listing.to_dict(), context, debug=True)
					finally:
						await browser.close()

	asyncio.run(test("keywords"))
