import requests, const

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
	def __init__(self, make, model, syear = None, eyear = None, bodystyle = None, trans = None, query = None):
		self.make = make
		self.model = model
		self.syear = syear
		self.eyear = eyear
		self.bodystyle = bodystyle
		self.trans = trans
		self.query = query
	
	""" 
	We're probably only using this and __hash__ for the google search cache,
	which is only being used for BaT and carsandbids, so no need to add year,
	bodystyle, etc.
	"""
	def __eq__(self, other):
		if isinstance(other, Car):
			return (self.make==other.make and self.model==other.model)
		return False

	def __hash__(self):
		return hash((self.make, self.model))
	
	def get_query(self):
		"""
		Uses the Google Search API to fetch urls for BaT and cars&bids listing
		pages, saving us the work of hardcoding each edge-case url (there are
		many!)

		Returns:
			URLs of BaT and Cars&Bids for the specific make/model/generation, as a
			tuple of strings with BaT first.
		"""
		q = f"{self.make} {self.model} bringatrailer carsandbids"
		params = {
			'key': const.GOOGLE_API_KEY,
			'cx': '620f99273bef84934', # my unique search engine key-- use this
			'q': q
		}
		res = requests.get("https://www.googleapis.com/customsearch/v1?", params=params)
		print(res.json())

		# upon query success, increment today's api calls count, formatted as
		# "Today's Google API use count: "
		with open("../keys/api_uses.txt", 'r+') as f:
			s = str(f.read())
			count = int(s[30:])
			count += 1
			s = s[:30] + str(count)
			f.write(s)
