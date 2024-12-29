from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from threading import Lock
import bs4, listing

def get_cars_and_bids_results(out, lock):

	options = Options()
	options.headless = True
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	driver.get("https://carsandbids.com/search/porsche/991-911/")

	WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CLASS_NAME, "auctions-list"))
	)

	soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
	
	items = soup.select('.auctions-list:not(.past-auctions)')
	for item in items:
		title = item.select_one('a.hero')['title']
		subtitle = item.select_one('p.auction-subtitle').text.strip()
		time = item.select_one('li.time-left .value').text.strip()
		image = item.select_one('img')['src']
		url = "https://carsandbids.com" + item.select_one('a.hero')['href']
		bid = item.select_one('span.bid-value').text.strip()

		key = "Cars & Bids: " + title
		with lock:
			out[key] = listing.Listing(title, url, image, time, bid)
		
		# print(f"Title: {title}")
		# # print(f"Subtitle: {subtitle}")
		# print(f"URL: {url}")
		# # print(f"Image URL: {image}")
		# print(f"Current Bid: {bid}")
		# print(f"Time Remaining: {time}")
		# print("-" * 40)

	driver.quit()

if __name__ == "__main__":
	out = {}
	lock = Lock()
	get_cars_and_bids_results(out, lock)