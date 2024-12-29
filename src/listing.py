class Listing:
	def __init__(self, title, url, image, time, price):
		self.title 	= title
		self.url 	= url
		self.image 	= image
		self.time 	= time
		self.price 	= price

	def __str__(self):
		return f"Title: {self.title}\nURL: {self.url}\nImage URL: {self.image}\nCurrent Bid: {self.price}\nTime Remaining: {self.time}"