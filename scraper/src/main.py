import asyncio
from playwright.async_api import async_playwright
import listing, cars_and_bids, pcarmarket, bring_a_trailer
from quart import Quart, request, jsonify
from quart_cors import cors

app = Quart(__name__)
app = cors(app)

async def run_scrapers(make, model, generation):
	"""Run all scrapers asynchronously and return combined results"""
	async with async_playwright() as p:
		browser = await p.chromium.launch(
			headless=True,
			args=[
				'--no-sandbox',
				'--disable-setuid-sandbox',
				'--disable-dev-shm-usage',
				'--disable-accelerated-2d-canvas',
				'--no-first-run',
				'--no-zygote',
				'--disable-gpu',
				'--disable-web-security',
				'--disable-features=VizDisplayCompositor'
			]
		)
		
		context = await browser.new_context(
			user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			viewport={'width': 1920, 'height': 1080},
			locale='en-US',
			timezone_id='America/New_York'
		)
		
		try:
			car = listing.Car(make, model, generation)
			results = await asyncio.gather(
				bring_a_trailer.get_results(car, context),
				pcarmarket.get_results(car, context),
				cars_and_bids.get_results(car, context)
			)
		finally:
			await browser.close()
		
		# Combine results
		combined = {}
		for result_dict in results:
			combined.update(result_dict)
		
		return combined

@app.route("/search", methods=["GET"])
async def get():
	make = request.args.get("make")
	model = request.args.get("model")
	generation = request.args.get("generation")
	
	# Make sure at least these parameters exist
	if not make or not model:
		return jsonify({"error": "Missing parameters"}), 400
	
	try:
		results = await run_scrapers(make, model, generation)
		
		# Convert to serializable format if needed
		serializable_results = {}
		for key, value in results.items():
			if hasattr(value, '__dict__'):
				serializable_results[key] = value.__dict__
			else:
				serializable_results[key] = value
		
		return jsonify(serializable_results)
	
	except Exception as e:
		return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
	app.run(debug=True, port=5000)