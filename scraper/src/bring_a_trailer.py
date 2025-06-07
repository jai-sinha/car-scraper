from playwright.sync_api import sync_playwright
import listing
from datetime import datetime, timezone
from threading import Lock
from urllib.parse import quote

def countdown(url, browser):
	"""
	Calculates remaining time from specified end time in human readable format.
	Opens a separate page because we have to go into the listing to get the time--
	not scrapable from the main page.
	
	Args:
		url: Specific listing containing auction end time info.
	Returns:
		Remaining time from now until end time in human readable format.
	"""

	page = browser.new_page()
	
	try:
		page.goto(url, timeout=30000)
		
		# Get the data-until attribute value using JavaScript
		data_until = page.evaluate("""
				() => {
					const countdown = document.querySelector('.listing-available-countdown');
					return countdown ? countdown.getAttribute('data-until') : null;
				}
		""")
		
		# maybe replace this with pandas?
		if data_until:
				end_time = datetime.fromtimestamp(int(data_until), timezone.utc)
				now = datetime.now(timezone.utc)
				time_left = (end_time - now).total_seconds()
				
				if time_left > 0:
					hours, remainder = divmod(time_left, 3600)
					minutes, seconds = divmod(remainder, 60)
					if hours > 24:
						days = hours/24
						return f"{int(days)}d"
					elif hours < 1:
						return f"{int(minutes)}m {int(seconds)}s"
					else:
						return f"{int(hours)}h {int(minutes)}m"
				else:
					return "Auction ended"
		else:
				print("Countdown element not found")
				return "0"
				
	except Exception as e:
		print(f"Error fetching countdown for BaT: {e}")
		return "Error"


def get_results(car: listing.Car, out: dict, lock: Lock):
	"""
	Fetches search results from bring a trailer for a given car, extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		out: Shared dictionary with listing details.
		lock: Threading lock.
	"""
	q = quote(car.make), quote(car.generation), quote(car.model)
	q = "+".join(q)
	search_url = "https://bringatrailer.com/auctions/?search=" + q
	
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		page = browser.new_page()
		
		try:
			page.goto(search_url, timeout=30000)
			
			# check filter input value to confirm search filtering has occurred
			search_terms = f"{car.make} {car.generation} {car.model}"
			page.wait_for_function(
				f'''
				document.querySelector("input[data-bind=\\"textInput: filterTerm\\"]").value.includes("{search_terms}")
				''',
				timeout=6000
			)

			page.wait_for_selector('.listing-card', timeout=10000)

			listings_data = page.evaluate("""
				() => {
					const cards = document.querySelectorAll('.listing-card');
					return Array.from(cards).map(card => ({
						title: card.querySelector('h3')?.textContent?.trim() || '',
						url: card.href || '',
						image: card.querySelector('.thumbnail img')?.src || '',
						bid: card.querySelector('.bidding-bid .bid-formatted')?.textContent?.trim() || 'No bid'
					}));
				}
			""")
			
			print(f"Found {len(listings_data)} listings")
			
			for data in listings_data:
				if not data['title'] or not data['url']:
					continue
					
				# Clean up bid text
				bid = data['bid']
				if bid.startswith("USD "):
					bid = bid[4:]
				
				# Get countdown time
				time_remaining = countdown(data['url'], browser)
				
				# Store in shared dictionary
				key = "BaT: " + data['title']
				with lock:
					out[key] = listing.Listing(key, data['url'], data['image'], time_remaining, bid)
				
				print(f"Title: {data['title']}")
				print(f"URL: {data['url']}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {time_remaining}")
				print("-" * 40)
					
		except Exception as e:
			print(f'Error fetching BaT results: {e}')
		finally:
			browser.close()

if __name__ == "__main__":
	out = {}
	lock = Lock()
	car = listing.Car("Porsche", "911", "991")
	get_results(car, out, lock)
	