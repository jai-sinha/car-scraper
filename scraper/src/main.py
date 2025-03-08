import listing, const, cars_and_bids, pcarmarket, bring_a_trailer
import threading
from flask import Flask, request, jsonify
from diskcache import Cache

# shouldn't need FanoutCache because cache isn't used in threads
cache = Cache(const.CACHE_DIR)
app = Flask(__name__)

@app.route("/search", methods=["GET"])
def get():
	make = request.args.get("make") 
	model = request.args.get("model")
	generation = request.args.get("generation")

	# make sure at least these three parameters exist (for now)
	if not make or not model or not generation:
		return jsonify({"error": "Missing parameters"}), 400 

	car = listing.Car(make, model, generation=generation)
	if car in cache:
		car.query = cache[car]

	out = {}
	lock = threading.Lock()

	# init threads
	bat = threading.Thread(target=bring_a_trailer.get_results, args=(car, out, lock))
	cb = threading.Thread(target=cars_and_bids.get_results, args=(car, out, lock))
	pcar = threading.Thread(target=pcarmarket.get_results, args=(car, out, lock))

	if car not in cache:
		cache.add(car, car.query)

	# start and join threads
	cb.start()
	pcar.start()
	bat.start()
	cb.join()
	pcar.join()
	bat.join()

	# jsonify response
	return jsonify({key: value.__dict__ for key, value in out.items()})

if __name__ == "__main__":
	app.run(debug=True, port=5000)