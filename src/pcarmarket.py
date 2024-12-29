import requests, bs4, listing
from datetime import datetime
from threading import Lock

def countdown(ends_at):
	end_time = datetime.utcfromtimestamp(int(ends_at))
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
		return "DT"


def get_pcarmarket_results(out, lock):
	
	res = requests.get("https://www.pcarmarket.com/search/?q=911")
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
		
		bid = (
			item.select_one('.buyNowHomeDetails').text.strip() 
			if item.select_one('.buyNowHomeDetails') 
			else item.select_one('.auction-bid').text.strip()
			)

		time = item.select_one('.countdownTimer')
		if time:
			ends_at = time.get('data-ends-at')
			time = countdown(ends_at)
		else:
			time = "DT"

		key = "PCARMARKET: " + title
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
	get_pcarmarket_results(out, lock)