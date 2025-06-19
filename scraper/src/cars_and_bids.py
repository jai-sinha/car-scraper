from playwright.sync_api import sync_playwright
from urllib.parse import quote
from threading import Lock
import listing

def get_results(car: listing.Car, out: dict, lock: Lock):
	"""
	Fetches search results from Cars & Bids for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		out: Shared dictionary with listing details.
		lock: Threading lock.
	"""

	# encode car info for url
	q = quote(car.make), quote(car.generation), quote(car.model)
	q = "%20".join(q)
	search_url = "https://carsandbids.com/search?q=" + q
	print(search_url)

	with sync_playwright() as p:

		# avoid headless detection (important!!)
		browser = p.chromium.launch(
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
		context = browser.new_context(
			user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			viewport={'width': 1920, 'height': 1080},
			locale='en-US',
			timezone_id='America/New_York'
		)
    
		page = context.new_page()
		
		try:
			page.goto(search_url, timeout=2000)
			page.wait_for_selector("ul.auctions-list", timeout=2000)

			# html_content = page.content()
			# print("FULL PAGE HTML:")
			# print(html_content)

			# Extract the data
			listings_data = page.evaluate("""
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
			
			# Process each listing, all live listings and the 30 most recent closed
			# will be visible, so remove the closed ones from the count/processing
			print(f"Found {len(listings_data) - 30} auction listings")
			for data in listings_data:
				if not data['title'] or not data['timeRemaining']:
					continue
				
				# Create listing
				key = "C&B: " + data['title']
				url = "carsandbids.com" + data['url']
				with lock:
					out[key] = listing.Listing(key, url, data['image'], data['timeRemaining'], data['bid'])
				
				
				# Print extracted data
				# print(f"Title: {data['title']}")
				# print(f"URL: {url}")
				# print(f"Image URL: {data['image']}")
				# print(f"Current Bid: {data['bid']}")
				# print(f"Time Remaining: {data['timeRemaining']}")
				# print("-" * 50)

		except Exception as e:
			print(f"Error scraping auctions: {e}")
			return []
		
		finally:
			browser.close()

if __name__ == "__main__":
	out = {}
	lock = Lock()
	car = listing.Car("BMW", "M3", "E90")
	get_results(car, out, lock)