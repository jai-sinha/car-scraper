from playwright.async_api import async_playwright, Page, BrowserContext
from datetime import datetime, timezone
from typing import Dict, Optional, List
import re
import listing
import asyncio

TIMEOUT = 15000
BASE_URL = "https://www.pcarmarket.com"

class PCarMarketScraper:
	"""Scraper for PCAR Market auction listings."""
	
	@staticmethod
	def _extract_year(title: str) -> Optional[int]:
		"""Extract year from listing title."""
		year_match = re.search(r'\b(19|20)\d{2}\b', title)
		return int(year_match.group(0)) if year_match else None
	
	@staticmethod
	def _format_marketplace_listing(data: Dict) -> tuple:
		"""Format marketplace listing data."""
		bid = f"{data['buyNow']} (MarketPlace)"
		end_time = "N/A"
		title = data['title'][13:]  # Remove "MarketPlace " prefix
		return bid, end_time, title
	
	@staticmethod
	def _format_auction_listing(data: Dict) -> tuple:
		"""Format auction listing data."""
		bid = data['bid']
		end_time = datetime.fromtimestamp(int(data['timeRemaining']), timezone.utc)
		title = data['title']
		return bid, end_time, title
	
	@staticmethod
	async def _extract_search_listings(page: Page) -> List[Dict]:
		"""Extract listing data from search results page."""
		return await page.evaluate("""
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
	
	@staticmethod
	async def _extract_live_listings(page: Page) -> List[Dict]:
		"""Extract listing data from live auctions page."""
		return await page.evaluate("""
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
	
	@staticmethod
	def _process_listing_data(data: Dict) -> Optional[listing.Listing]:
		"""Process raw listing data into Listing format."""
		if not data['title'] or not data['url']:
			return None
		
		year = PCarMarketScraper._extract_year(data['title'])
		
		# Handle marketplace vs auction listings
		if data['title'].startswith("MarketPlace"):
			bid, end_time, title = PCarMarketScraper._format_marketplace_listing(data)
		else:
			if not data['timeRemaining']:
				return None
			bid, end_time, title = PCarMarketScraper._format_auction_listing(data)
		
		url = f"{BASE_URL}{data['url']}"
		key = f"PCAR: {title}"
		
		return listing.Listing(
			key, 
			url, 
			data['image'], 
			end_time, 
			bid, 
			year
		)



async def get_results(query: str, browser, debug: bool = False) -> Dict:
	"""
	Fetches search results from PCAR Market for a given query.

	Args:
		query: The desired car to search, formatted as a URL-encoded string
		browser: Playwright async browser
		debug: Print debug information
	
	Returns:
		Dictionary of discovered listings
	"""
	search_url = f"{BASE_URL}/search/?q={query}"
	
	if debug:
		print(f"Searching: {search_url}")

	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)

		# Wait for results or no results message
		await page.wait_for_function(
			"""() => {
				return document.querySelector('.post.clearfix.searchResult') !== null ||
					document.body.textContent.includes('No results were found in auctions matching your query');
			}""",
			timeout=TIMEOUT
		)
		
		# Check if any results exist
		if not await page.query_selector('.post.clearfix.searchResult'):
			if debug:
				print("No listings found")
			return {}

		# Extract and process listings
		listings_data = await PCarMarketScraper._extract_search_listings(page)
		
		if debug:
			print(f"Found {len(listings_data)} auction listings")

		results = {}
		for data in listings_data:
			processed = PCarMarketScraper._process_listing_data(data)
			if processed:
				results[processed.url] = processed.to_dict()
				
				if debug:
					print(processed)
					print("-" * 50)

		return results

	except Exception as e:
		print(f"Error scraping PCAR auctions: {e}")
		return {}
	finally:
		await page.close()


async def get_all_live(context: BrowserContext, debug: bool = False) -> Dict:
	"""
	Fetches all live auctions from PCAR Market.

	Args:
		context: Playwright async browser context
		debug: Print debug information
	
	Returns:
		Dictionary of all live listings
	"""
	search_url = f"{BASE_URL}/auction/all/?page=1"
	page = await context.new_page()
	
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		await page.wait_for_function(
			"() => document.querySelector('.post.car') !== null",
			timeout=TIMEOUT
		)

		results = {}
		page_num = 1
		
		while True:
			if debug:
					print(f"Scraping page {page_num}")

			await page.wait_for_selector('.post.car', timeout=TIMEOUT)
			listings_data = await PCarMarketScraper._extract_live_listings(page)

			if debug:
					print(f"Found {len(listings_data)} auction listings on page {page_num}")

			for data in listings_data:
				processed = PCarMarketScraper._process_listing_data(data)
				if processed:
					results[processed.url] = processed.to_dict()
					
					if debug:
						print(processed)
						print("-" * 50)

			# Check for next page
			has_next = await page.evaluate("""
				() => {
					const nextLi = document.querySelector('li.next:not(.disabled)');
					return !!(nextLi && nextLi.querySelector('a'));
				}
			""")
			
			if has_next:
				await page.click('li.next:not(.disabled) a')
				await page.wait_for_load_state('domcontentloaded', timeout=TIMEOUT)
				page_num += 1
			else:
				break

		if debug:
			print(f"Total listings found: {len(results)}")

		return results

	except Exception as e:
		print(f"Error scraping PCAR auctions: {e}")
		return {}
	finally:
		await page.close()


async def get_listing_details(title: str, url: str, context: BrowserContext, debug: bool = False) -> None:
	"""
	Fetches details and keywords for a specific listing from PCAR Market.

	Args:
		title: The title of the listing
		url: The URL of the listing
		context: Playwright async browser context
		debug: Print debug information
	Returns:
		Keywords extracted from the listing
	"""
	page = await context.new_page()
	
	try:
		await page.goto(url, timeout=TIMEOUT)
		await page.wait_for_selector('#auction-details-list', timeout=TIMEOUT)

		listing_keywords = await page.evaluate("""
			() => {
				const facts = {};
				document.querySelectorAll('#auction-details-list li').forEach(li => {
					const strong = li.querySelector('strong');
					if (strong) {
						const key = strong.textContent.replace(':', '').trim();
						const value = li.textContent.replace(strong.textContent, '').replace(':', '').trim();
						facts[key] = value;
					}
				});
				return {
					model: facts['Model'] || null
				};
			}
		""")

		# Update listing with keywords
		kw = [ 
			listing_keywords.get("model", ""),
			title.replace(".", " ")
		]
		
		if debug:
			print(f"Keywords for {title}: {kw}")

		return " ".join(filter(None, kw))

	except Exception as e:
		print(f'Error fetching PCAR details for {title}: {e}')
	finally:
		await page.close()

# Test functions
async def _test_results():
	"""Test the search results functionality."""
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		try:
			from urllib.parse import quote
			query = quote("Porsche 911 991")
			await get_results(query, browser, debug=True)
		finally:
			await browser.close()


async def _test_live():
	"""Test the live auctions functionality."""
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		context = await browser.new_context(viewport={"width": 800, "height": 600})
		
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
		browser = await p.chromium.launch(headless=True)
		context = await browser.new_context(viewport={"width": 800, "height": 600})
		
		await context.route(
			"**/*", 
			lambda route, request: route.abort() 
			if request.resource_type in ["image", "media", "font"] 
			else route.continue_()
		)
		
		try:
			test_url = "https://www.pcarmarket.com/auction/2018-porsche-911-gt3-touring-13/"
			test_listing = listing.Listing(
					"3,300-MILE 2018 PORSCHE 991.2 GT3 TOURING", 
					test_url, "", "", "", 2020
			).to_dict()
			await get_listing_details(test_listing, context, debug=True)
		finally:
			await context.close()
			await browser.close()


if __name__ == "__main__":
	# Available tests: "results", "live", "keywords"
	asyncio.run(_test_results())