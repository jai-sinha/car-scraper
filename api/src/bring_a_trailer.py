from playwright.async_api import async_playwright
import re
import asyncio
import listing
from datetime import timezone, datetime, timedelta

TIMEOUT = 10000

async def get_results(query, browser, debug=False):
	"""
	Fetches search results from bring a trailer for a given car, extracts listing details, and stores them in a dictionary.

	Args:
		query: The desired car to search, formatted as a URL-encoded string.
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

			# Extract year from title using regex
			year_match = re.search(r'\b(19|20)\d{2}\b', data['title'])
			year = int(year_match.group(0)) if year_match else None
				
			# Clean up bid text
			bid = str(data['bid'])
			if bid.startswith("USD "):
				bid = bid[4:]

			# Format time, removing seconds
			timeRemaining = str(data['timeRemaining'])
			if "day" in timeRemaining: # Keep days as-is (e.g., "1 day", "2 days")
				pass
			elif ":" in timeRemaining: # Handle time formats like "1:23:45" or "23:45"
				parts = timeRemaining.split(":")
				if len(parts) == 3:  # hours:minutes:seconds
					timeRemaining = f"{parts[0]}h {parts[1]}m"
				elif len(parts) == 2:  # minutes:seconds
					timeRemaining = f"{parts[0]}m"
			else: # No colons and no days means just seconds remaining
				timeRemaining = "0m"
			
			# Create listing
			key = "BaT: " + data['title']
			out[key] = listing.Listing(key, data['url'], data['image'], timeRemaining, bid, year)
			
			if debug:
				print(f"Title: {data['title']}")
				print(f"URL: {data['url']}")
				print(f"Year: {year}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {timeRemaining}")
				print("-" * 50)

		# Return dict of BaT results
		return out				

	except Exception as e:
		print(f'Error fetching BaT results: {e}')
		return {}


async def get_all_live(context, debug=False):
	"""
	Fetches all live auctions from Bring a Trailer and returns them as a dict.
	
	Args:
		context: Playwright async browser context
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""
	search_url = "https://bringatrailer.com/auctions/"
	page = await context.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		

		# Then confirm there are live auctions matching the filter
		await page.wait_for_function(
			"""() => {
					return document.querySelector('.listing-card') ||
							document.querySelector('#auctions_filtered_message_none');
			}""",
			timeout=TIMEOUT
		)
		
		# Scroll to load all listings
		for _ in range(25):
			count = await page.evaluate("document.querySelectorAll('.listing-card').length")
			await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
			await asyncio.sleep(1)  # Give browser time to render to deal w CPU limits
			
			try:
				await page.wait_for_function(
					f"document.querySelectorAll('.listing-card').length > {count}",
					timeout=3000
				)
			except: break # If no new listings loaded, we're done scrolling

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

		scrape_time = datetime.now(timezone.utc)
		out = {}
		for data in listings_data:
			if not data['title'] or not data['url']:
				continue

			# Extract year from title using regex
			year_match = re.search(r'\b(19|20)\d{2}\b', data['title'])
			year = int(year_match.group(0)) if year_match else None
				
			# Clean up bid text, removing currency code prefix
			bid = str(data['bid'])[4:]

			# Process end time in UTC
			timeRemaining = str(data['timeRemaining'])
			if "day" in timeRemaining.lower(): # Keep days as-is (e.g., "1 day", "2 days")
				delta = timedelta(days=int(timeRemaining.split()[0]))
			elif ":" in timeRemaining: # Handle time formats like "1:23:45" or "23:45"
				parts = timeRemaining.split(":")
				if len(parts) == 3:  # hours:minutes:seconds
					delta = timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=int(parts[2]))
				elif len(parts) == 2:  # minutes:seconds
					delta = timedelta(minutes=int(parts[0]), seconds=int(parts[1]))
			elif "ended" in timeRemaining.lower():
				delta = timedelta(seconds=2) # Give a small buffer for ended auctions
			else: # No colons and no days means just seconds remaining
				delta = timedelta(seconds=int(timeRemaining.split('s')[0]))

			end_time = scrape_time + delta
			
			# Create listing
			out[data['url']] = listing.Listing(f"BaT: {data['title']}", data['url'], data['image'], end_time, bid, year).to_dict()
		
			if debug:
				print(f"Title: {data['title']}")
				# print(f"URL: {data['url']}")
				print(f"Year: {year}")
				print(f"Current Bid: {bid}")
				print(f"End Time: {end_time.isoformat()}")
				print("-" * 50)

		# Return dict of BaT results
		return out				

	except Exception as e:
		print(f'Error fetching BaT results: {e}')
		return {}


async def get_listing_details(listing: listing.Listing, context, debug=False):
	"""
	Fetches details and keywords for a specific listing from Bring a Trailer.

	Args:
		listing: The listing object to fetch details for.
		context: Playwright async context
		debug: Print all info
	Returns:
		A modified listing dictionary with keywords added.
	"""
	try:
		page = await context.new_page()
		await page.goto(listing.url, timeout=TIMEOUT)
		await page.wait_for_selector('.column-groups', timeout=TIMEOUT)

		# Get make, model from the detail page 
		listing_keywords = await page.evaluate("""
			() => {
				const keywords = [];
				const keywordElements = Array.from(document.querySelectorAll('.group-item-wrap .group-item')).slice(0, 2);
				keywordElements.forEach(el => {
					const label = el.querySelector('.group-title-label');
					let value = '';
					if (label) {
						let node = label.nextSibling;
						while (node) {
							if (node.nodeType === Node.TEXT_NODE) {
									value += node.textContent;
							}
							node = node.nextSibling;
						}
					} else {
						value = el.innerText;
					}
					if (value) {
						// Only keep the part before the first parenthesis, if present
						value = value.split('(')[0].trim();
						if (value) {
							keywords.push(value);
						}
					}
				});
				return keywords;
			}
		""")

		# Add keywords including title to the listing object
		listing.keywords.extend(listing_keywords)
		listing.keywords.append(listing.title)

		if debug:
			print(f"Keywords for {listing.title}: {listing.keywords}")

	except Exception as e:
		print(f'Error fetching BaT details for {listing.title}: {e}')
		return
	
	finally:
		await page.close()

if __name__ == "__main__":
	async def test(test_type):
		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)

			match test_type:
				case "results":
					try:
						from urllib.parse import quote
						query = quote("911 991")
						await get_results(query, browser, debug=True)

					finally:
						await browser.close()

				case "live":
					context = await browser.new_context()
					try:
						await get_all_live(context, debug=True)

					finally:
						await browser.close()

				case "keywords":
					context = await browser.new_context()
					try:
						# Example listing, replace with actual URL
						url = "https://bringatrailer.com/listing/2005-porsche-911-carrera-coupe-44/"
						test_listing = listing.Listing("2015 porsche 911 carrera coupe", url, "","", "", 2020)
						await get_listing_details(test_listing, context, debug=True)

					finally:
						await browser.close()
	
	asyncio.run(test("keywords"))
	