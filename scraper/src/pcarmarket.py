from playwright.async_api import async_playwright
from datetime import datetime, timezone
import asyncio
import listing

TIMEOUT = 10000

async def get_results(query, browser, debug=False):
	"""
	Fetches search results from pcarmarket for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search, formatted as a URL-encoded string.
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
			
			# Check if this is a live auction
			if data['bid']: 
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
			out[key] = listing.Listing(key, url, data['image'], timeRemaining, bid)
			
			if debug:
				print(f"Title: {title}")
				print(f"URL: {url}")
				print(f"Image URL: {data['image']}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {timeRemaining}")
				print("-" * 50)

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
	async def test():
		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)

			try:
				from urllib.parse import quote
				query = quote("Porsche 911 991")
				await get_results(query, browser, debug=True)

			finally:
				await browser.close()
	
	asyncio.run(test())
