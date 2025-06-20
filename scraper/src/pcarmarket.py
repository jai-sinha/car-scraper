from playwright.async_api import async_playwright
from datetime import datetime, timezone
from urllib.parse import quote
import asyncio
import listing

TIMEOUT = 10000

def countdown(ends_at):
	"""
	Calculates remaining time from specified end time in human readable format.

	Args:
		ends_at: Time at which countdown ends at in unix time format.

	Returns:
		Time remaining in auction as a D/HH/MM/SS string
	"""
	end_time = datetime.fromtimestamp(int(ends_at), timezone.utc)
	now = datetime.now(timezone.utc)
	time_left = (end_time - now).total_seconds()

	hours, remainder = divmod(time_left, 3600)
	minutes, seconds = divmod(remainder, 60)
	if hours > 24:
		days = hours/24
		return f"{int(days)} days"
	elif hours < 1:
		return f"{int(minutes)} minutes"
	else:
		return f"{int(hours)}:{int(minutes)}"


async def get_results(car: listing.Car, browser):
	"""
	Fetches search results from pcarmarket for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		browser: Playwright async browser
	Returns:
		All discovered listings as a dict
	"""
	# print(car.make, car.model, car.generation)
	q = quote(car.make), quote(car.generation), quote(car.model)
	q = "%20".join(q)
	search_url = "https://www.pcarmarket.com/search/?q=" + q
	print(search_url)

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		await page.wait_for_selector('.post.clearfix.searchResult', timeout=TIMEOUT)

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
			
			# print(f"Title: {title}")
			# print(f"URL: {url}")
			# print(f"Image URL: {data['image']}")
			# print(f"Current Bid: {bid}")
			# print(f"Time Remaining: {timeRemaining}")
			# print("-" * 50)

		# Return dict of PCAR results
		return out

	except Exception as e:
		print(f"Error scraping PCAR auctions: {e}")
		return {}
	

if __name__ == "__main__":
	async def test():
		async with async_playwright() as p:
			browser = await p.chromium.launch(headless=True)

			try:
				car = listing.Car("Porsche", "911", "991")
				result = await get_results(car, browser)

			finally:
				await browser.close()
	
	asyncio.run(test())
