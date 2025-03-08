import requests, bs4, listing, const
from datetime import datetime, timezone
from threading import Lock

def get_query(car: listing.Car):
	"""
	Uses the Google Search API to fetch BaT URL for the car, saving us the the work of hardcoding each niche edge-case URL that may come up
	
	Returns:
		BaT URL for the given car as as string
	"""
	q = f"bringatrailer {car.make} {car.generation} {car.model} for sale"
	params = {
		'key': const.GOOGLE_API_KEY,
		'cx': '620f99273bef84934', # my unique search engine key--use this
		'q': q
	}
	res = requests.get("https://www.googleapis.com/customsearch/v1?", params=params)
	# print(res.json())
	results = res.json()
	for item in results['items']:
		"""
		Check custom search results until the correct link is found, using the car's generation to find matches if possible or its model if not
		"""
		if car.generation and car.generation.casefold() in item['title'].casefold():
			return item['link']
		elif car.model.casefold() in item['title'].casefold():
			return item['link']
		
	raise Exception(f"Matching page wasn't found. Possible input error?\n{results}")

def countdown(url):
	"""
	Calculates remaining time from specified end time in human readable format.

	Args:
		url: Specific listing containing auction end time info.

	Returns:
		Remaining time from now until end time in human readable format.
	"""
	res = requests.get(url)
	try:
		res.raise_for_status()
	except Exception as e:
		print("Error fetching countdown for BaT: %s" %e)

	soup = bs4.BeautifulSoup(res.text, 'html.parser')

	countdown_element = soup.select_one('.listing-available-countdown')
	if countdown_element:
		data_until = countdown_element.get('data-until')
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
				return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
		else:
			return "Auction ended"
	else:
		print("Element not found")
		return 0
	
def get_results(car: listing.Car, out: dict, lock: Lock):
	"""
	Fetches search results from bring a trailer for a given car, extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		out: Shared dictionary with listing details.
		lock: Threading lock.
	"""
	q = car.query if car.query else get_query(car)
	res = requests.get(q)
	try:
		res.raise_for_status()
	except Exception as e:
		print('Error fetching BaT results: %s' %e)

	soup = bs4.BeautifulSoup(res.text, 'html.parser')
	items = soup.select('.listing-card')
	for item in items:
		title = item.select_one('h3 a').text.strip()
		url = item.select_one('h3 a')['href']
		image = item.select_one('.thumbnail img')['src']
		bid = item.select_one('.bidding-bid .bid-formatted').text.strip()
		time = countdown(url)

		key = "BaT: " + title
		with lock:
			out[key] = listing.Listing(title, url, image, time, bid)

		# print(f"Title: {title}")
		# print(f"URL: {url}")
		# print(f"Current Bid: {bid}")
		# print(f"Time Remaining: {time}")
		# print("-" * 40)
	
if __name__ == "__main__":
	out = {}
	lock = Lock()
	car = listing.Car("Porsche", "911", "991")
	get_results(car, out, lock)
