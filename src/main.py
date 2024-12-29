import cars_and_bids, pcarmarket, bring_a_trailer, threading
from threading import Lock

out = {}
lock = Lock()
bat = threading.Thread(target=bring_a_trailer.get_bring_a_trailer_results(out, lock))
crsnbds = threading.Thread(target=cars_and_bids.get_cars_and_bids_results(out, lock))
pcar = threading.Thread(pcarmarket.get_pcarmarket_results(out, lock))

crsnbds.start()
pcar.start()
bat.start()
pcar.join()
bat.join()
crsnbds.join()
for item in out:
	print(item)
	print("-" * 80)