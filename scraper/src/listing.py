class Listing:
	def __init__(self, title, url, image, time, price, year):
		self.title 	= title
		self.url 	= url
		self.image 	= image
		self.time 	= time
		self.price 	= price
		self.year 	= year

	def __str__(self):
		return f"Title: {self.title}\nURL: {self.url}\nCurrent Bid: {self.price}\nTime Remaining: {self.time}"
