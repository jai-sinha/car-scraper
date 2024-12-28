import requests, bs4
from datetime import datetime

def countdown(url):
	res = requests.get(url)
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
	
def get_bring_a_trailer_results():
	out = {}

	res = requests.get("https://bringatrailer.com/porsche/991-911/")
	try:
		res.raise_for_status()
	except Exception as e:
		print('There was a problem: %s' %e)

	soup = bs4.BeautifulSoup(res.text, 'html.parser')

	live = soup.select('.listings-container.items-container.auctions-grid .listing-card')
	for listing in live:
		title = listing.select_one('h3 a').text.strip()
		url = listing.select_one('h3 a')['href']
		image = listing.select_one('.thumbnail img')['src']
		bid = listing.select_one('.bidding-bid .bid-formatted').text.strip()
		time = countdown(url)

		out[title] = {
			"title": title,
			"subtitle": "",
			"url": url,
			"image": image,
			"bid": bid,
			"time": time
			}
		

		print(f"Title: {title}")
		print(f"URL: {url}")
		# print(f"Image URL: {image}")
		print(f"Current Bid: {bid}")
		print(f"Time Remaining: {time}")
		print("-" * 40)
	
	return out

if __name__ == "__main__":
	get_bring_a_trailer_results()

