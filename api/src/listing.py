class Listing:
	def __init__(self, title: str, url: str, image: str, time, price: str, year: int, keywords=None):
		self.title 	= title
		self.url 	= url
		self.image 	= image
		self.time 	= time
		self.price 	= price
		self.year 	= year
		self.keywords = keywords or []

	def __str__(self):
		return f"Title: {self.title}\nURL: {self.url}\nCurrent Bid: {self.price}\nEnd Time (UTC): {self.time}"

	# Convert to dictionary for JSON serialization
	def to_dict(self):
		return {
			"title": self.title,
			"url": self.url,
			"image": self.image,
			"time": self.time,
			"price": self.price,
			"year": self.year,
			"keywords": self.keywords
		}