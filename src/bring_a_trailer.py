import requests, bs4, listing
from datetime import datetime
from threading import Lock

def countdown(url):
	res = requests.get(url)
	try:
		res.raise_for_status()
	except Exception as e:
		print("Error fetching countdown for BaT: %s" %e)

	soup = bs4.BeautifulSoup(res.text, 'html.parser')

	countdown_element = soup.select_one('.listing-available-countdown')
	if countdown_element:
		data_until = countdown_element.get('data-until')
		end_time = datetime.utcfromtimestamp(int(data_until))
		now = datetime.utcnow()
		time_left = end_time - now

		if time_left.total_seconds() > 0:
			hours, remainder = divmod(time_left.total_seconds(), 3600)
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
	
def get_bring_a_trailer_results(out, lock):

	res = requests.get("https://bringatrailer.com/porsche/991-911/")
	try:
		res.raise_for_status()
	except Exception as e:
		print('Error fetching BaT results: %s' %e)

	soup = bs4.BeautifulSoup(res.text, 'html.parser')

	items = soup.select('.listings-container.items-container.auctions-grid .listing-card')
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
		# # print(f"Image URL: {image}")
		# print(f"Current Bid: {bid}")
		# print(f"Time Remaining: {time}")
		# print("-" * 40)
	


if __name__ == "__main__":
	out = {}
	lock = Lock()
	get_bring_a_trailer_results(out, lock)

