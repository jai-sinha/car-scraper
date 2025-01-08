import listing, const, cars_and_bids, pcarmarket, bring_a_trailer, ebay
import threading
from diskcache import Cache

# shouldn't need FanoutCache because cache isn't used in threads
cache = Cache(const.CACHE_DIR)
car = listing.Car("Porsche", "991 911")
if car in cache:
	car.query = cache[car]
else:
	query_results = car.get_query()
	cache.add(car, query_results)

out = {}
lock = threading.Lock()

bat = threading.Thread(bring_a_trailer.get_results(car, out, lock))
crsnbds = threading.Thread(cars_and_bids.get_results(car, out, lock))
pcar = threading.Thread(pcarmarket.get_results(car, out, lock))
eby = threading.Thread(ebay.get_results(car, out, lock))

# threading to increase efficiency in getting/scraping urls
crsnbds.start()
pcar.start()
bat.start()
eby.start()
crsnbds.join()
pcar.join()
bat.join()
eby.join()

for item in out:
	print(item)
	print("-" * 80)