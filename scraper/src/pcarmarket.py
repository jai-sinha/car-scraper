from playwright.async_api import async_playwright
from datetime import datetime, timezone
import re
import listing
import asyncio

TIMEOUT = 10000

async def get_results(query, browser, debug=False):
	"""
	Fetches search results from pcarmarket for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		query: The desired car to search, formatted as a URL-encoded string.
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""

	# Encode car info for url
	search_url = "https://www.pcarmarket.com/search/?q=" + query
	if debug:
		print(search_url)

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)

		# Check to see if any results exist
		await page.wait_for_function(
			"""() => {
				return document.querySelector('.post.clearfix.searchResult') !== null ||
					document.body.textContent.includes('No results were found in auctions matching your query');
			}""",
			timeout=TIMEOUT
		)
		
		# If there were no results, simply return an empty dict
		if not await page.query_selector('.post.clearfix.searchResult'):
			if debug:
				print("No listings found")
			return {}
		

		listings_data = await page.evaluate("""
			() => {
			const items = document.querySelectorAll('.post.clearfix.searchResult');
			return Array.from(items).map(item => ({
				title: item.querySelector('h2 a')?.textContent?.trim() || '',
				url: item.querySelector('h2 a')?.getAttribute('href') || '',
				bid: item.querySelector('.auction-bid strong')?.nextSibling?.textContent?.trim() || '',
				buyNow: item.querySelector('.buyNowHomeDetails strong')?.nextSibling?.textContent?.trim() || '',
				timeRemaining: (() => {
					const countdown = item.querySelector('.countdownTimer');
					return countdown ? countdown.getAttribute('data-ends-at') : null;
				})(),
				image: item.querySelector('img.feat_img')?.getAttribute('src') || ''
			}));
			}
		""")

		# Process each listing
		if debug:
			print(f"Found {len(listings_data)} auction listings")

		out = {}
		for data in listings_data:
			if not data['title'] or not data['url']:
				continue
			
			# Extract year from title using regex
			year_match = re.search(r'\b(19|20)\d{2}\b', data['title'])
			year = int(year_match.group(0)) if year_match else None

			# Check if this is a live auction
			if not data['title'].startswith("MarketPlace"):
				bid = data['bid']
				timeRemaining = countdown(data['timeRemaining'])
				title = data['title']

			# Or if it's in MarketPlace
			else:
				bid = f"{data['buyNow']} (MarketPlace)"
				timeRemaining = "N/A"
				title = data['title'][13:]

			# Create listing
			url = f"https://pcarmarket.com{data['url']}"
			key = f"PCAR: {title}"
			out[key] = listing.Listing(key, url, data['image'], timeRemaining, bid, year).to_dict()
			
			if debug:
				print(f"Title: {title}")
				print(f"URL: {url}")
				print(f"Year: {year}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {timeRemaining}")
				print("-" * 50)

		# Return dict of PCAR results
		return out

	except Exception as e:
		print(f"Error scraping PCAR auctions: {e}")
		return {}

async def get_all_live(browser, debug=False):
	"""
	Fetches all live auctions from PCARMARKET, and returns them as a dict.

	Args:
		browser: Playwright async browser
		debug: Print all info
	Returns:
		All discovered listings as a dict
	"""

	search_url = "https://www.pcarmarket.com/auction/all/?page=1"

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		await page.wait_for_function(
			"""() => {
				return document.querySelector('.post.car') !== null
			}""",
			timeout=TIMEOUT
		)

		listings_data = await page.evaluate("""
			() => {
			const items = document.querySelectorAll('.post.car');
			return Array.from(items).map(item => ({
				title: item.querySelector('h2 a')?.textContent?.trim() || '',
				url: item.querySelector('h2 a')?.getAttribute('href') || '',
				bid: item.querySelector('.auction-bid .pushed_bid_amount')?.textContent?.trim() || '',
				buyNow: item.querySelector('.buyNowHomeDetails strong')?.nextSibling?.textContent?.trim() || '', // fallback, if needed
				timeRemaining: (() => {
					const countdown = item.querySelector('.countdownTimer');
					return countdown ? countdown.getAttribute('data-ends-at') : null;
				})(),
				image: item.querySelector('img.featured')?.getAttribute('src') || ''
			}));
			}
		""")

		out = {}
		page_num = 1
		while True:
			if debug:
				print(f"Scraping page {page_num}")

			listings_data = await page.evaluate("""
				() => {
				const items = document.querySelectorAll('.post.car');
				return Array.from(items).map(item => ({
					title: item.querySelector('h2 a')?.textContent?.trim() || '',
					url: item.querySelector('h2 a')?.getAttribute('href') || '',
					bid: item.querySelector('.auction-bid .pushed_bid_amount')?.textContent?.trim() || 'No bids',
					buyNow: item.querySelector('.buyNowHomeDetails strong')?.nextSibling?.textContent?.trim() || '',
					timeRemaining: (() => {
						const countdown = item.querySelector('.countdownTimer');
						return countdown ? countdown.getAttribute('data-ends-at') : null;
					})(),
					image: item.querySelector('img.featured')?.getAttribute('src') || ''
				}));
				}
			""")

			if debug:
				print(f"Found {len(listings_data)} auction listings on page {page_num}")

			for data in listings_data:
				if not data['title'] or not data['url']:
					continue

				# Extract year from title using regex
				year_match = re.search(r'\b(19|20)\d{2}\b', data['title'])
				year = int(year_match.group(0)) if year_match else None

				bid = data['bid']
				end_time = datetime.fromtimestamp(int(data['timeRemaining']), timezone.utc)
				title = data['title']

				# Create listing
				url = f"https://pcarmarket.com{data['url']}"
				key = f"PCAR: {title}"
				out[key] = listing.Listing(key, url, data['image'], end_time, bid, year).to_dict()
				
				if debug:
					print(f"Title: {title}")
					print(f"URL: {url}")
					print(f"Year: {year}")
					print(f"Current Bid: {bid}")
					print(f"Time Remaining: {end_time}")
					print("-" * 50)

			# Check for next page button using li.next:not(.disabled) a
			has_next = await page.evaluate("""
				() => {
					const nextLi = document.querySelector('li.next:not(.disabled)');
					return !!(nextLi && nextLi.querySelector('a'));
				}
			""")
			if has_next:
				await page.click('li.next:not(.disabled) a')
				await page.wait_for_load_state('networkidle')
				page_num += 1
			else:
				break

		# Return dict of PCAR results
		return out

	except Exception as e:
		print(f"Error scraping PCAR auctions: {e}")
		return {}

def countdown(ends_at):
	"""
	Calculates remaining time from specified end time in human readable format.

	Args:
		ends_at: Time at which countdown ends at in unix time format.

	Returns:
		Time remaining in auction as a formatted string
	"""
	end_time = datetime.fromtimestamp(int(ends_at), timezone.utc)
	now = datetime.now(timezone.utc)
	time_left = (end_time - now).total_seconds()

	hours, remainder = divmod(time_left, 3600)
	minutes, _ = divmod(remainder, 60)
	if hours > 48:
		days = hours/24
		return f"{int(days)} days"
	elif hours > 24:
		return "1 day"
	elif hours < 1:
		return f"{int(minutes)}m"
	else:
		return f"{int(hours)}h {int(minutes)}m"

if __name__ == "__main__":
	async def test(isSearch: bool):
		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)
			if isSearch:
				try:
					from urllib.parse import quote
					query = quote("Porsche 911 991")
					await get_results(query, browser, debug=True)

				finally:
					await browser.close()
			else:
				try:
					results = await get_all_live(browser, debug=True)
					print(f"Found {len(results)} live auctions")
				finally:
					await browser.close()

	asyncio.run(test(False))
