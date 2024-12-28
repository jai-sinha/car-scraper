from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_cars_and_bids_results():
	out = {}

	options = Options()
	options.headless = True
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	driver.get("https://carsandbids.com/search/porsche/991-911/")

	WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CLASS_NAME, "auctions-list"))
	)

	soup = BeautifulSoup(driver.page_source, 'html.parser')
	
	listings = soup.select('.auctions-list:not(.past-auctions)')
	for listing in listings:
		title = listing.select_one('a.hero')['title']
		subtitle = listing.select_one('p.auction-subtitle').text.strip()
		time = listing.select_one('li.time-left .value').text.strip()
		image = listing.select_one('img')['src']
		url = "https://carsandbids.com" + listing.select_one('a.hero')['href']
		bid = listing.select_one('span.bid-value').text.strip()

		out[title] = {
			"title": title,
			"subtitle": subtitle,
			"url": url,
			"image": image,
			"bid": bid,
			"time": time
			}
		
		print(f"Title: {title}")
		print(f"Subtitle: {subtitle}")
		print(f"URL: {url}")
		# print(f"Image URL: {image}")
		print(f"Current Bid: {bid}")
		print(f"Time Remaining: {time}")
		print("-" * 40)

	driver.quit()
	return out

if __name__ == "__main__":
	get_cars_and_bids_results()