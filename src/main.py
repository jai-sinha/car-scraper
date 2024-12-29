import listing, cars_and_bids, pcarmarket, bring_a_trailer 
import sys, threading

car = listing.Car("BMW", "E36 M3")
out = {}
lock = threading.Lock()

bat = threading.Thread(target=bring_a_trailer.get_bring_a_trailer_results(car, out, lock))
crsnbds = threading.Thread(target=cars_and_bids.get_cars_and_bids_results(car, out, lock))
pcar = threading.Thread(pcarmarket.get_pcarmarket_results(car, out, lock))

crsnbds.start()
pcar.start()
bat.start()
crsnbds.join()
pcar.join()
bat.join()

for item in out:
	print(item)
	print("-" * 80)