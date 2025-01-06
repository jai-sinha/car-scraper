import requests, json, const

class Listing:
	def __init__(self, title, url, image, time, price, subtitle = None, dt_highbid = None):
		self.title 	= title
		self.url 	= url
		self.image 	= image
		self.time 	= time
		self.price 	= price
		self.subtitle = subtitle
		self.dt_highbid = dt_highbid

	def __str__(self):
		return f"Title: {self.title}\nURL: {self.url}\nImage URL: {self.image}\nCurrent Bid: {self.price}\nTime Remaining: {self.time}"

class Car:
	def __init__(self, make, model, generation=None, syear=None, eyear=None, bodystyle=None, trans=None, query=None):
		"""
		All fields are strings except the query, which is a size 2 tuple of strings, and only 
		make/model are required because the rest aren't all used on every site.

		make: company that produces the car (e.g. Porsche)
		model: specific model (e.g. 911)
		generation: name of a specific generation, used on C&B, BaT, and PCAR (991 for a Porsche 911)
		syear: starting year of search range
		eyear: ending year of search range
		bodystyle: e.g. coupe, convertible, sedan (for cars that have multiple options)
		trans: transmission type, manual or automatic
		query: tuple of urls to scrape for this specific car on C&B and BaT

		"""
		self.make = make
		self.model = model
		self.generation = generation
		self.syear = syear
		self.eyear = eyear
		self.bodystyle = bodystyle
		self.trans = trans
		self.query = query
	
	""" 
	We're probably only using this and __hash__ for the google search cache,
	which is only being used for BaT and carsandbids, so no need to add year,
	bodystyle, etc. but generation is required.
	"""
	def __eq__(self, other):
		if isinstance(other, Car):
			return (self.make==other.make and self.model==other.model and self.generation==other.generation)
		return False

	def __hash__(self):
		return hash((self.make, self.model, self.generation))
	
	def get_query(self):
		"""
		Uses the Google Search API to fetch urls for BaT and cars&bids listing
		pages, saving us the work of hardcoding each edge-case url of which there
		are many. Runs two searches, one for BaT and one for C&B to make the
		result scraping easier.
		
		Returns:
			URLs of BaT and Cars&Bids for the specific make/model/generation, as a
			tuple of strings with BaT first.
		"""
		urls = ("","")

		# Run the BaT search, save result
		q = f"{self.make} {self.generation} {self.model} for sale bringatrailer"
		params = {
			'key': const.GOOGLE_API_KEY,
			'cx': '620f99273bef84934', # my unique search engine key-- use this
			'q': q
		}
		res = requests.get("https://www.googleapis.com/customsearch/v1?", params=params)
		print(res.json())

		results = json.loads(res.json())
		for items in results['items']:
			# TODO: find the url that corresponds to the BaT page for this car,
			# and insert into urls[0]
			pass

		# Run the C&B search, save result
		q = f"{self.make} {self.generation} {self.model} for sale carsandbids"
		res = requests.get("https://www.googleapis.com/customsearch/v1?", params=params)
		print(res.json())

		results = json.loads(res.json())
		for items in results['items']:
			# TODO: find the url that corresponds to the C&B page for this car,
			# and insert into urls[1]
			pass

		# upon query success, increment today's api calls count, formatted as
		# "Today's Google API use count: "
		with open("../keys/api_uses.txt", 'r+') as f:
			s = str(f.read())
			count = int(s[30:])
			count += 1
			s = s[:30] + str(count)
			f.write(s)

		# once both urls are found, save them in the car's query field
		self.query = urls
