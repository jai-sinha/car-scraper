import requests, bs4, listing
from datetime import datetime
from threading import Lock

def query(car: listing.Car) -> str:
	model = car.model.lower().strip().replace(" ", "+")
	make = car.make.lower()
	out = "https://www.pcarmarket.com/search/?q=" + make + "+" + model
	return out

def countdown(ends_at):
	end_time = datetime.utcfromtimestamp(int(ends_at))
	now = datetime.utcnow()
	time_left = end_time - now

	hours, remainder = divmod(time_left.total_seconds(), 3600)
	minutes, seconds = divmod(remainder, 60)
	if hours > 24:
		days = hours/24
		return f"{int(days)}d"
	elif hours < 1:
		return f"{int(minutes)}m {int(seconds)}s"
	else:
		return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def dt_highbid(url):
	res = requests.get(url)
	try:
		res.raise_for_status()
	except Exception as e:
		print("Error fetching PCARMARKET high bid: %s" %e)
	
	soup = bs4.BeautifulSoup(res.text, 'html.parser')
	bid = soup.select_one('.pushed_bid_amount').text.strip()
	return bid

def get_pcarmarket_results(car, out, lock):
	q = query(car)
	res = requests.get(q)
	try:
		res.raise_for_status()
	except Exception as e:
		print("Error fetching PCARMARKET results: %s" %e)
	
	soup = bs4.BeautifulSoup(res.text, 'html.parser')

	items = soup.select('.post.clearfix.searchResult')
	for item in items:
		title = item.select_one('h2 a').text.strip()
		url = "https://www.pcarmarket.com" + item.select_one('h2 a')['href']
		image = item.select_one('.feat_img')['src']
		
		key = "PCARMARKET: " + title
		# if DT, get Buy Now price, high bid
		if "DT" in title:
			buyNow = item.select_one('.buyNowHomeDetails').text.strip()
			highBid = dt_highbid(url)
			with lock:
				out[key] = listing.Listing(title, url, image, "DT", buyNow, dt_highbid=highBid)

		# else, just get high bid and time remaining
		else:
			bid = item.select_one('.auction-bid').text.strip()
			ends_at = time.get('data-ends-at')
			time = countdown(ends_at)
			with lock:
				out[key] = listing.Listing(title, url, image, time, bid)
		
		# print(f"Title: {title}")
		# print(f"URL: {url}")
		# # print(f"Image URL: {image}")
		# print(f"{bid}")
		# print(f"Time Left: {time}")
		# print("-" * 40)

if __name__ == "__main__":
	out = {}
	lock = Lock()
	car = listing.Car("Porsche", "991 911")
	get_pcarmarket_results(car, out, lock)