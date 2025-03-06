import listing, const, cars_and_bids, pcarmarket, bring_a_trailer
import threading
from diskcache import Cache

# shouldn't need FanoutCache because cache isn't used in threads
cache = Cache(const.CACHE_DIR)
car = listing.Car("Porsche", "911", generation="991")
if car in cache:
	car.query = cache[car]
else:
	car.get_query()
	cache.add(car, car.query)

out = {}
lock = threading.Lock()

bat = threading.Thread(bring_a_trailer.get_results(car, out, lock))
crsnbds = threading.Thread(cars_and_bids.get_results(car, out, lock))
pcar = threading.Thread(pcarmarket.get_results(car, out, lock))

# threading to increase efficiency in getting/scraping urls
crsnbds.start()
pcar.start()
bat.start()
crsnbds.join()
pcar.join()
bat.join()

for item in out:
	print(item)
	print("-" * 80)