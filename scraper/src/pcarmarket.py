from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from threading import Lock
from urllib.parse import quote
import listing

def countdown(ends_at):
	"""
	Calculates remaining time from specified end time in human readable format.

	Args:
		ends_at: Time at which countdown ends at in unix time format.

	Returns:
		Remaining time from now until end time in human readable format.
	"""
	end_time = datetime.fromtimestamp(int(ends_at), timezone.utc)
	now = datetime.now(timezone.utc)
	time_left = (end_time - now).total_seconds()

	hours, remainder = divmod(time_left, 3600)
	minutes, seconds = divmod(remainder, 60)
	if hours > 24:
		days = hours/24
		return f"{int(days)}d"
	elif hours < 1:
		return f"{int(minutes)}m"
	else:
		return f"{int(hours)}h {int(minutes)}m"

# def dt_highbid(url):
# 	"""
# 	Fetches the current highest bid for a listing in "DT" format.

# 	Args:
# 		url: pcarmarket url for "DT" car.

# 	Returns:
# 		The highest bid.
# 	"""
# 	res = requests.get(url)
# 	try:
# 		res.raise_for_status()
# 	except Exception as e:
# 		print("Error fetching PCARMARKET high bid: %s" %e)
	
# 	soup = bs4.BeautifulSoup(res.text, 'html.parser')
# 	bid = soup.select_one('.pushed_bid_amount').text.strip()
# 	return bid

def get_results(car: listing.Car, out: dict, lock: Lock):
	"""
	Fetches search results from pcarmarket for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		out: Shared dictionary with listing details.
		lock: Threading lock.
	"""
	# print(car.make, car.model, car.generation)
	q = quote(car.make), quote(car.generation), quote(car.model)
	q = "%20".join(q)
	search_url = "https://www.pcarmarket.com/search/?q=" + q
	print(search_url)

	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		page = browser.new_page()

		try:
			page.goto(search_url, timeout=10000)
			page.wait_for_selector('.post.clearfix.searchResult', timeout=2000)

			listings_data = page.evaluate("""
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
			for data in listings_data:
				if not data['title'] or not data['url']:
					continue
				
				# Check if this is a live auction or in MarketPlace
				timeRemaining = "N/A"
				bid = f"{data['buyNow']} (MarketPlace)"
				if data['bid']:
					bid = data['bid']
					timeRemaining = countdown(data['timeRemaining'])

				title = data['title'][13:] if data['title'].startswith("MarketPlace: ") else data['title']
				
				# Create listing
				key = "PCAR: " + title
				with lock:
					out[key] = listing.Listing(key, data['url'], data['image'], timeRemaining, bid)
				
				# Print extracted data
				print(f"Title: {title}")
				print(f"URL: {data['url']}")
				print(f"Current Bid: {bid}")
				print(f"Time Remaining: {timeRemaining}")
				print("-" * 50)

		except Exception as e:
			print(f"Error scraping auctions: {e}")
			return []
		
		finally:
			browser.close()

if __name__ == "__main__":
	out = {}
	lock = Lock()
	car = listing.Car("Porsche", "911", "991")
	get_results(car, out, lock)

	# for item in items:
	# 	title = item.select_one('h2 a').text.strip()
	# 	url = "https://www.pcarmarket.com" + item.select_one('h2 a')['href']
	# 	image = item.select_one('.feat_img')['src']
		
	# 	key = "PCARMARKET: " + title
	# 	# if DT, get Buy Now price, high bid
	# 	if "DT" in title:
	# 		buyNow = item.select_one('.buyNowHomeDetails').text.strip()
	# 		highBid = dt_highbid(url)
	# 		buyNow = buyNow[buyNow.find("$"):] # remove the text that says "high bid" or "buy now"
	# 		with lock:
	# 			out[key] = listing.Listing(key, url, image, "DT", buyNow, dt_highbid=highBid)

	# 	# else, just get high bid and time remaining
	# 	else:
	# 		bid = item.select_one('.auction-bid').text.strip()
	# 		# this would return "." when there are no bids, we want ""
	# 		bid = bid[bid.find("$"):] if bid.find("$") > 0 else "" 
	# 		countdown_element = soup.select_one('.countdownTimer')
	# 		ends_at = countdown_element.get('data-ends-at')
	# 		time = countdown(ends_at)
	# 		with lock:
	# 			out[key] = listing.Listing(key, url, image, time, bid)
		
		# print(f"Title: {title}")
		# print(f"URL: {url}")
		# # print(f"Image URL: {image}")
		# print(f"{bid}")
		# print(f"Time Left: {time}")
		# print("-" * 40)