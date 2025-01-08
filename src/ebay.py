import requests, bs4, listing
from datetime import datetime, timezone
from threading import Lock
import const

def countdown(end_time):
    """
	Calculates remaining time from specified end time in human readable format.

	Args:
		end_time: The time the auction ends.

	Returns:
		Remaining time from now until end time in human readable format.
	"""

    end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
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

def get_results(car: listing.Car, out: dict, lock: Lock):
    """
	Fetches search results from eBay for a given car,
	extracts listing details, and stores them in a shared dictionary.

	Args:
		car: The desired car to search.
		out: Shared dictionary with listing details.
		lock: Threading lock.
	"""
     
	# eBay Browse API endpoint for search
    api_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    query_params = {
        "q": f"{car.make} {car.model}",
        "category_ids": 6001,
        #"filters": "categoryIds:{6001}, conditionIds:{1000|3000|4000}",  # Category 6001 is for "eBay Motors"
        "limit": "20"  # Number of listings to fetch
    }

    # Set up headers with authorization
    headers = {
        "Authorization": f"Bearer {const.EBAY_API_KEY}",
        "Content-Type": "application/json",
        "X-EBAY-C-MARKETPLACE-ID" : "EBAY_US"
    }

    # Make the request
    response = requests.get(api_url, headers=headers, params=query_params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(f"{car.make} {car.model} Listings from eBay:")
        for item in data.get("itemSummaries", []):
            title = item.get("title", "N/A")
            price = item.get("price", {}).get("value", "N/A")
            currency = item.get("price", {}).get("currency", "N/A")
            url = item.get("itemWebUrl", "N/A")
            buying_options = item.get("buyingOptions", [])
            end_time = item.get("itemEndDate", "N/A")
            image= item.get("image", {}).get("imageUrl", "N/A")

            is_auction = "AUCTION" in buying_options

            print(f"Title: {title}")
            print(f"Price: {price} {currency}")
            print(f"URL: {url}")
            print(f"Auction: {'Yes' if is_auction else 'No'}")
            time = 0
            if is_auction and end_time != "N/A":
                time = countdown(end_time)
                print(f"Auction Ends: {time}")
                
            key = "eBay: " + title
            with lock:
                out[key] = listing.Listing(title, url, image, time, price)
    else:
        print(f"Failed to fetch listings: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
	out = {}
	lock = Lock()
	car = listing.Car("Tesla", "3")
	get_results(car, out, lock)