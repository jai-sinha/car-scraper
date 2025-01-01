import requests, bs4

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
	
	def query(self, site):
		search_term = f"{site}+{self.make}"
		for term in self.model.split():
			search_term+= f"+{term}"
		
		res = requests.get(f"https://www.google.com/search?q={search_term}")
		soup = bs4.BeautifulSoup(res.text, 'html.parser')
		# first h3 is the first search result item, go back 3 parents to get its href
		# can't find the url directly because all div classes are nonsense
		search = soup.select_one('h3')

		# url comes with nonsense attached to back, '/url?q=' attached to front,
		# nonsense at the end starts with '&' so this just cleans it up.
		# cleaning up could also be done with re library and "https[^&]*" but this
		# way is quicker (i think) and doesn't require another library.

		url = search.parent.parent.parent['href']
		return url[7:url.find('&')]
