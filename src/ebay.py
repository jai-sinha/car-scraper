import requests, bs4

def get_ebay_results():
	res = requests.get("https://www.ebay.com/sch/i.html?_from=R40&_nkw=Porsche+911&_sacat=6001&_stpos=53711&Model%2520Year=2011%7C2012%7C2013%7C2014%7C2015&_fspt=1&UF_single_selection=Make%3APorsche%2CModel%3A911&UF_context=finderType%3AVEHICLE_FINDER&rt=nc&Transmission=Manual&_dcat=10156")

	try:
		res.raise_for_status()
	except Exception as e:
		print("Error fetching eBay results: %s" %e)
	
	soup = bs4.BeautifulSoup(res.text, 'html.parser')
	listings = soup.select(".s-item.s-item__pl-on-bottom")
	print(listings[1])
	print("-" * 40)
	print(listings[2])

if __name__ == '__main__':
	get_ebay_results()
