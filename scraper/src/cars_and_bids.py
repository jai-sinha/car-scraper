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
		browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-blink-features=AutomationControlled'])
		page = browser.new_page()
		
		try:
			page.goto(search_url, timeout=500)
			page.set_extra_http_headers({
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
			})

			page.wait_for_selector("ul.auctions-list", timeout=5000)
			page.wait_for_selector("li.auction-item", timeout=5000)

			# Extract the data
			listings_data = page.evaluate("""
				() => {
					const items = document.querySelectorAll('ul.auctions-list li.auction-item');
					return Array.from(items).map(item => ({
						title: item.querySelector('a.hero')?.getAttribute('title') || '',
						url: item.querySelector('a.hero')?.getAttribute('href') || '',
						bid: item.querySelector('.bid-value')?.textContent?.trim() || '',
						timeRemaining: item.querySelector('.time-left .value')?.textContent?.trim() || ''
					}));
				}
			""")
			# Wait for auction items to load
			# page.wait_for_selector("ul.auctions-list li", timeout=5000)
			
			# # Extract auction data
			# listings_data = page.evaluate("""
			# 	() => {
			# 		const items = document.querySelectorAll('.auction-item');
			# 		return Array.from(items).map(item => {
			# 			// Get the main link element
			# 			const heroLink = item.querySelector('a.hero');
						
			# 			// Extract title from the hero link or metadata section
			# 			const titleFromHero = heroLink?.getAttribute('title') || '';
			# 			const titleFromMetadata = item.querySelector('.auction-title a')?.textContent?.trim() || '';
			# 			const title = titleFromHero || titleFromMetadata;
						
			# 			// Extract URL
			# 			const url = heroLink?.getAttribute('href') || 
			# 							item.querySelector('.auction-title a')?.getAttribute('href') || '';
						
			# 			// Extract image
			# 			const image = item.querySelector('img')?.getAttribute('src') || '';
						
			# 			// Extract current bid
			# 			const bidElement = item.querySelector('.bid-value');
			# 			const bid = bidElement?.textContent?.trim() || 'No bid';
						
			# 			// Extract time remaining
			# 			const timeElement = item.querySelector('.time-left .value');
			# 			const timeRemaining = timeElement?.textContent?.trim() || 'Unknown';
						
			# 			// Extract location
			# 			const location = item.querySelector('.auction-loc')?.textContent?.trim() || '';
						
			# 			// Extract subtitle/description
			# 			const subtitle = item.querySelector('.auction-subtitle')?.textContent?.trim() || '';
						
			# 			// Check if inspected
			# 			const isInspected = item.querySelector('.inspected') !== null;
						
			# 			return {
			# 				title: title,
			# 				url: url.startsWith('http') ? url : `https://carsandbids.com${url}`,
			# 				image: image,
			# 				bid: bid,
			# 				timeRemaining: timeRemaining,
			# 				location: location,
			# 				subtitle: subtitle,
			# 				isInspected: isInspected
			# 			};
			# 		});
			# 	}
			# """)
				
			print(f"Found {len(listings_data)} auction listings")
			
			# Process each listing
			for data in listings_data:
				if not data['title'] or not data['url']:
					continue
				
				# Clean up bid text
				bid = data['bid']
				if bid.startswith("$"):
					# Remove $ and any commas
					bid = bid.replace("$", "").replace(",", "")
				
				# Create listing key
				key = "C&B: " + data['title']
				with lock:
					out[key] = listing.Listing(key, data['url'], data['image'], data['timeRemaining'], bid)
				
				
				# Print extracted data
				print(f"Title: {data['title']}")
				print(f"URL: {data['url']}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {data['timeRemaining']}")
				print(f"Location: {data['location']}")
				print(f"Subtitle: {data['subtitle']}")
				print(f"Inspected: {data['isInspected']}")
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