from playwright.async_api import async_playwright, Page, BrowserContext
import re
import asyncio
import listing
from datetime import timezone, datetime, timedelta
from typing import Dict, Optional, List
from urllib.parse import quote

TIMEOUT = 15000
BASE_URL = "https://bringatrailer.com"

class BringATrailerScraper:
	"""Scraper for Bring a Trailer auction listings."""
	
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
			return None  # Remove ended auctions from results
		else:
			# Just seconds remaining
			seconds = int(time_str.split('s')[0])
			return timedelta(seconds=seconds)
	
	@staticmethod
	def _extract_year(title: str) -> Optional[int]:
		"""Extract year from listing title."""
		year_match = re.search(r'\b(19|20)\d{2}\b', title)
		return int(year_match.group(0)) if year_match else None
	
	@staticmethod
	def _clean_bid(bid_str: str) -> str:
		"""Clean bid string by removing currency prefix."""
		return bid_str[4:] if bid_str.startswith("USD ") else bid_str
	
	@staticmethod
	async def _extract_listings_data(page: Page) -> List[Dict]:
		"""Extract listings data from page using JavaScript."""
		return await page.evaluate("""
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
	
	@staticmethod
	def _process_listing_data(data: Dict, scrape_time: datetime) -> Optional[listing.Listing]:
		"""Process raw listing data into Listing object."""
		if not data['title'] or not data['url']:
			return None
		
		year = BringATrailerScraper._extract_year(data['title'])
		bid = BringATrailerScraper._clean_bid(str(data['bid']))
		
		try:
			# Extract end time from time remaining
			delta = BringATrailerScraper._parse_time_remaining(data['timeRemaining'])
			if delta is None:
				return None
			end_time = scrape_time + delta
		except (ValueError, IndexError) as e:
			return None
		
		return listing.Listing(
			f"BaT: {data['title']}", 
			data['url'], 
			data['image'], 
			end_time, 
			bid, 
			year
		)

async def get_results(query: str, browser, debug: bool = False) -> Dict:
	"""
	Fetches search results from Bring a Trailer for a given query.

	Args:
		query: The desired car to search, formatted as a URL-encoded string.
		browser: Playwright async browser
		debug: Print debug information
	
	Returns:
		Dictionary of discovered listings
	"""
	# Encode car info for URL, BaT uses "+" instead of "%20"
	query = query.replace("%20", "+")
	search_url = f"{BASE_URL}/auctions/?search={query}"
	
	if debug:
		print(f"Searching: {search_url}")
	
	page = await browser.new_page()
	try:
		await page.goto(search_url, timeout=TIMEOUT)
		
		# Wait for search filtering to complete
		search_terms = query.replace('+', ' ')
		await page.wait_for_function(
			f'document.querySelector("input[data-bind=\\"textInput: filterTerm\\"]").value.includes("{search_terms}")',
			timeout=TIMEOUT
		)

		# Wait for listings or no results message
		await page.wait_for_function(
			"""() => document.querySelector('.listing-card') || 
						document.querySelector('#auctions_filtered_message_none')""",
			timeout=TIMEOUT
		)
		
		# Check if any listings exist
		if not await page.query_selector('.listing-card'):
			if debug:
					print("No listings found")
			return {}

		# Extract and process listings
		listings_data = await BringATrailerScraper._extract_listings_data(page)
		
		if debug:
			print(f"Found {len(listings_data)} listings")

		scrape_time = datetime.now(timezone.utc)
		results = {}
		
		for data in listings_data:
			processed = BringATrailerScraper._process_listing_data(data, scrape_time)
			if processed:
				results[processed.url] = processed.to_dict()
				
				if debug:
					print(processed)
					print("-" * 50)

		return results

	except Exception as e:
		print(f'Error fetching BaT results: {e}')
		return {}
	finally:
		await page.close()


async def get_all_live(context: BrowserContext, debug: bool = False) -> Dict:
	"""
	Fetches all live auctions from Bring a Trailer.
	
	Args:
		context: Playwright async browser context
		debug: Print debug information
	
	Returns:
		Dictionary of all live listings
	"""
	search_url = f"{BASE_URL}/auctions/"
	page = await context.new_page()
	
	try:
		await page.goto(search_url, timeout=TIMEOUT)

		# Wait for listings to load
		await page.wait_for_function(
			"""() => document.querySelector('.listing-card') || 
						document.querySelector('#auctions_filtered_message_none')""",
			timeout=TIMEOUT
		)
		
		# Scroll to load all listings
		await _scroll_to_load_all_listings(page)

		# Extract and process listings
		listings_data = await BringATrailerScraper._extract_listings_data(page)
		
		if debug:
			print(f"Found {len(listings_data)} total listings")

		scrape_time = datetime.now(timezone.utc)
		results = {}
		
		for data in listings_data:
			processed = BringATrailerScraper._process_listing_data(data, scrape_time)
			if processed:
				results[processed.url] = processed.to_dict()
				
				if debug:
					print(processed)
					print("-" * 50)

		return results

	except Exception as e:
		print(f'Error fetching BaT results: {e}')
		return {}
	finally:
		await page.close()


async def _scroll_to_load_all_listings(page: Page, max_attempts: int = 25) -> None:
	"""Scroll page to load all listings."""
	for attempt in range(max_attempts):
		count_before = await page.evaluate("document.querySelectorAll('.listing-card').length")
		await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
		
		try:
			await page.wait_for_function(
				f"document.querySelectorAll('.listing-card').length > {count_before}",
				timeout=3000
			)
		except:
			# No new listings loaded, we're done
			break


async def get_listing_details(title: str, url: str, page, debug: bool = False) -> None:
	"""
	Fetches details and keywords for a specific listing.

	Args:
		title: The title of the listing
		url: The URL of the listing
		page: Playwright async page
		debug: Print debug information
	Returns:
		Keywords extracted from the listing
	"""
	
	try:
		await page.goto(url, timeout=TIMEOUT)
		await page.wait_for_selector('.column-groups', timeout=TIMEOUT)

		# Extract keywords from listing page
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
						// Keep only the part before the first parenthesis
						value = value.split('(')[0].trim();
						if (value) {
								keywords.push(value);
						}
					}
				});

				return keywords;
			}
		""")

		# Update listing with keywords
		kw = []
		kw.extend(listing_keywords)
		kw.append(title)
		
		if debug:
			print(f"Keywords for {title}: {kw}")

		return " ".join(kw)

	except Exception as e:
		print(f'Error fetching BaT details for {title}: {e}')


# Test functions
async def _test_results():
	"""Test the search results functionality."""
	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		try:
			query = quote("911 991")
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
			url = "https://bringatrailer.com/listing/2005-porsche-911-carrera-coupe-44/"
			title = "2005 Porsche 911 Carrera Coupe 6-Speed"
			page = await context.new_page()
			await get_listing_details(title, url, page, debug=True)
		finally:
			await context.close()
			await browser.close()


if __name__ == "__main__":
	# Available tests: "results", "live", "keywords"
	asyncio.run(_test_keywords())