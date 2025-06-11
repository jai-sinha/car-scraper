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
		browser = p.chromium.launch(headless=False)
		page = browser.new_page()
		
		try:
			page.goto(search_url, timeout=500)
			page.wait_for_selector("ul.auctions-list", timeout=5000)

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
			
			# Process each listing
			print(f"Found {len(listings_data) - 30} auction listings")
			for data in listings_data:
				if not data['title'] or not data['url'] or not data['timeRemaining']:
					continue
				
				# Clean up bid text
				bid = data['bid']
				if bid.startswith("$"):
					# Remove $ and any commas
					bid = bid.replace("$", "").replace(",", "")
				
				# Create listing
				key = "C&B: " + data['title']
				with lock:
					out[key] = listing.Listing(key, data['url'], data['image'], data['timeRemaining'], bid)
				
				
				# Print extracted data
				print(f"Title: {data['title']}")
				print(f"URL: {data['url']}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {data['timeRemaining']}")
				print("-" * 50)

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