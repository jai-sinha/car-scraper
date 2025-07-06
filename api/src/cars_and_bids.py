from playwright.async_api import async_playwright, Page, BrowserContext
import re
import asyncio
import listing
from datetime import timezone, datetime, timedelta
from typing import Dict, Optional, List
from urllib.parse import quote

TIMEOUT = 15000
BASE_URL = "https://carsandbids.com"

class CarsAndBidsScraper:
	"""Scraper for Cars & Bids auction listings."""
	
	@staticmethod
	def _extract_year(title: str) -> Optional[int]:
		"""Extract year from listing title."""
		year_match = re.search(r'\b(19|20)\d{2}\b', title)
		return int(year_match.group(0)) if year_match else None

	
	@staticmethod
	def _parse_time_remaining(time_str: str) -> timedelta:
		"""Parse time remaining string into timedelta object."""
		time_str = time_str.lower().strip()
		
		if "day" in time_str:
			days = int(time_str.split()[0])
			return timedelta(days=days)
		elif ":" in time_str:
			parts = time_str.split(":")
			if len(parts) == 3:  # hours:minutes:seconds
					return timedelta(
						hours=int(parts[0]), 
						minutes=int(parts[1]), 
						seconds=int(parts[2])
					)
			elif len(parts) == 2:  # minutes:seconds
					return timedelta(
						minutes=int(parts[0]), 
						seconds=int(parts[1])
					)
		elif "ended" in time_str:
			return timedelta(seconds=2)  # Small buffer for ended auctions
		else:
			# Just seconds remaining
			seconds = int(time_str.split('s')[0])
			return timedelta(seconds=seconds)
	
	@staticmethod
	async def _extract_search_listings(page: Page) -> List[Dict]:
		"""Extract listing data from search results page."""
		return await page.evaluate("""
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
	
	@staticmethod
	async def _extract_live_listings(page: Page) -> List[Dict]:
		"""Extract listing data from live auctions page."""
		return await page.evaluate("""
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
	
	@staticmethod
	def _process_listing_data(data: Dict, scrape_time: datetime) -> Optional[listing.Listing]:
		"""Process raw live listing data into Listing object."""
		if not data['title'] or not data['timeRemaining']:
			return None
		
		year = CarsAndBidsScraper._extract_year(data['title'])
		
		try:
			delta = CarsAndBidsScraper._parse_time_remaining(data['timeRemaining'])
			end_time = scrape_time + delta
		except (ValueError, IndexError):
			return None
		
		url = f"{BASE_URL}{data['url']}"
		title = f"C&B: {data['title']}"
		
		return listing.Listing(
			title, 
			url, 
			data['image'], 
			end_time, 
			data['bid'], 
			year
		)


async def get_results(query: str, browser, debug: bool = False) -> Dict:
	"""
	Fetches search results from Cars & Bids for a given query.

	Args:
		query: The desired car to search, formatted as a URL-encoded string.
		browser: Playwright async browser
		debug: Print debug information
	
	Returns:
		Dictionary of discovered listings
	"""
	search_url = f"{BASE_URL}/search?q={query}"
	
	if debug:
		print(f"Searching: {search_url}")

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
		
		# Check if any results exist
		if not await page.query_selector('ul.auctions-list'):
			if debug:
					print("No listings found")
			return {}

		# Extract and process listings
		listings_data = await CarsAndBidsScraper._extract_search_listings(page)
		
		# Note: All live listings and the 30 most recent closed ones will be visible,
		# so we subtract 30 from the count for accurate live listing count
		if debug:
			print(f"Found {len(listings_data) - 30} auction listings")

		scrape_time = datetime.now(timezone.utc)
		results = {}

		for data in listings_data:
			processed = CarsAndBidsScraper._process_listing_data(data, scrape_time)
			if processed:
					results[processed.url] = processed.to_dict()
					
					if debug:
						print(processed)
						print("-" * 50)

		return results

	except Exception as e:
		print(f"Error scraping C&B auctions: {e}")
		return {}
	finally:
		await page.close()


async def get_all_live(context: BrowserContext, debug: bool = False) -> Dict:
	"""
	Fetches all live auctions from Cars & Bids.

	Args:
		context: Playwright async browser context
		debug: Print debug information
	
	Returns:
		Dictionary of all live listings
	"""
	search_url = BASE_URL
	page = await context.new_page()
	
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		await page.wait_for_function(
			"""() => {
					return document.querySelector('ul.auctions-list') !== null ||
							document.body.textContent.includes('No live auctions');
			}""",
			timeout=TIMEOUT
		)

		# Scroll to load all listings with improved logic
		await _scroll_to_load_all_listings(page)

		# Extract and process listings
		listings_data = await CarsAndBidsScraper._extract_live_listings(page)
		
		if debug:
			print(f"Found {len(listings_data)} auction listings")

		scrape_time = datetime.now(timezone.utc)
		results = {}
		
		for data in listings_data:
			processed = CarsAndBidsScraper._process_listing_data(data, scrape_time)
			if processed:
					results[processed.url] = processed.to_dict()
					
					if debug:
						print(processed)
						print("-" * 50)

		return results

	except Exception as e:
		print(f"Error scraping C&B auctions: {e}")
		return {}
	finally:
		await page.close()


async def _scroll_to_load_all_listings(page: Page) -> None:
	"""Scroll page to load all listings with controlled timing."""
	await page.evaluate("""
		() => {
			return new Promise(resolve => {
				let count = 0;
				const scrollStep = window.innerHeight;
				function scrollAndCheck() {
					window.scrollBy(0, scrollStep);
					setTimeout(() => {
						const items = document.querySelectorAll('ul.auctions-list li.auction-item').length;
						if (count < 50) { // Scroll 50 times, 10 page heights per second
							count++;
							scrollAndCheck();
						} else {
							resolve();
						}
					}, 100); // 10 page heights per second
				}
				scrollAndCheck();
			});
		}
	""")


async def get_listing_details(listing_dict: Dict, context: BrowserContext, debug: bool = False) -> None:
	"""
	Fetches details and keywords for a specific listing from Cars & Bids.

	Args:
		listing_dict: The listing dictionary to update with keywords
		context: Playwright async browser context
		debug: Print debug information
	"""
	page = await context.new_page()
	
	try:
		await page.goto(listing_dict["url"], timeout=TIMEOUT)
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

		kw = [
			listing_keywords.get("model", ""), 
			listing_dict["title"]
		]

		listing_dict["keywords"] = " ".join(filter(None, kw))

		if debug:
			print(f"Keywords for {listing_dict['title']}: {listing_dict['keywords']}")

	except Exception as e:
		print(f'Error fetching C&B details for {listing_dict["title"]}: {e}')
	finally:
		await page.close()


# Test functions
async def _test_results():
	"""Test the search results functionality."""
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True,
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
			viewport={'width': 800, 'height': 600},
			locale='en-US',
			timezone_id='America/New_York'
		)

		try:
			query = quote("997 911")
			await get_results(query, browser, debug=True)
		finally:
			await browser.close()


async def _test_live():
	"""Test the live auctions functionality."""
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True,
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
			viewport={'width': 800, 'height': 600},
			locale='en-US',
			timezone_id='America/New_York'
		)
		
		# Block unnecessary resources
		await context.route(
			"**/*", 
			lambda route, request: route.abort() 
			if request.resource_type in ["image", "media", "font"] 
			else route.continue_()
		)
		
		try:
			await get_all_live(context, debug=True)
		finally:
			await context.close()
			await browser.close()


async def _test_keywords():
	"""Test the keyword extraction functionality."""
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True,
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
			viewport={'width': 800, 'height': 600},
			locale='en-US',
			timezone_id='America/New_York'
		)
		
		await context.route(
			"**/*", 
			lambda route, request: route.abort() 
			if request.resource_type in ["image", "media", "font"] 
			else route.continue_()
		)
		
		try:
			url = "https://carsandbids.com/auctions/rx4XwZR0/2012-bmw-m3-coupe-competition-package"
			test_listing = listing.Listing(
					"2012 BMW M3 Coupe Competition Package", 
					url, "", "", "", 2012
			).to_dict()
			await get_listing_details(test_listing, context, debug=True)
		finally:
			await context.close()
			await browser.close()


if __name__ == "__main__":
	# Available tests: "results", "live", "keywords"
	asyncio.run(_test_live())