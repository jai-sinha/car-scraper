import requests, bs4

res = requests.get("https://www.google.com/search?q=bringatrailer+bmw+e90+m3")
soup = bs4.BeautifulSoup(res.text, 'html.parser')
# first h3 is the first search result item, go back 3 parents to get its href
# can't find the url directly because all div classes are nonsense
search = soup.select_one('h3')

# url comes with nonsense attached to back, '/url?q=' attached to front,
# nonsense at the end starts with '&' so this just cleans it up.
# cleaning up could also be done with re library and "https[^&]*" but this
# way is quicker (i think) and doesn't require another library.

url = search.parent.parent.parent['href']
url = url[7:url.find('&')]
print(url)

"""
Note on getting urls: For cars&bids and BaT, chassis codes like '991' or 'E90'
are used to specify model generation, and the urls reflect that. On PCAR it
doesn't really matter because it's a general search, but on all the other sites
they just go by model year instead of generation, so the searching is super
different and the urls we want to scrape are also super different.
"""