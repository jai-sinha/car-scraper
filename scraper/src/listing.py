from urllib.parse import quote

class Listing:
	def __init__(self, title, url, image, time, price):
		self.title 	= title
		self.url 	= url
		self.image 	= image
		self.time 	= time
		self.price 	= price

	def __str__(self):
		return f"Title: {self.title}\nURL: {self.url}\nImage URL: {self.image}\nCurrent Bid: {self.price}\nTime Remaining: {self.time}"

class Car:
	def __init__(self, make, model, generation=None):
		"""
		All fields are strings and only make/model are required because the rest aren't all used on every site.

		make: company that produces the car (e.g. Porsche)
		model: specific model (e.g. 911)
		generation: name of a specific generation, used on C&B, BaT, and PCAR (eg: 991 for a Porsche 911)
		"""
		self.make = make
		self.model = model
		self.generation = generation
