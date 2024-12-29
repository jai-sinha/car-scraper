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
	def __init__(self, make, model, syear = None, eyear = None, bodystyle = None, trans = None):
		self.make = make
		self.model = model
		self.syear = syear
		self.eyear = eyear
		self.bodystyle = bodystyle
		self.trans = trans

		if make == "Mercedes": make = "Mercedes-Benz"
