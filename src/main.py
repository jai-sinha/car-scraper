import listing, cars_and_bids, pcarmarket, bring_a_trailer
import threading
from diskcache import Cache

CACHE_DIR = ".car_cache" # make this a constant for use later(?)

cache = Cache(CACHE_DIR)
car = listing.Car("Porsche", "991 911")
if car in cache:
	car.query(cache[car])
else:
	query_results = car.get_query()
	cache.add(car, query_results)

out = {}
lock = threading.Lock()

bat = threading.Thread(bring_a_trailer.get_results(car, out, lock))
crsnbds = threading.Thread(cars_and_bids.get_results(car, out, lock))
pcar = threading.Thread(pcarmarket.get_results(car, out, lock))

crsnbds.start()
pcar.start()
bat.start()
crsnbds.join()
pcar.join()
bat.join()

for item in out:
	print(item)
	print("-" * 80)