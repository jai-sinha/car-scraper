import const, requests, pprint

make = "bmw"
model = "m3"
generation = "e90"


q = f"{make} {generation} {model} for sale carsandbids"
params = {
	'key': const.GOOGLE_API_KEY,
	'cx': '620f99273bef84934', # my unique search engine key-- use this
	'q': q
}
res = requests.get("https://www.googleapis.com/customsearch/v1?", params=params)
pprint.pp(res.json())

print("-" * 80)

topResult = res.json()['items'][0]
pprint.pp(topResult)

# upon query success, increment today's api calls count, formatted as
# "Today's Google API use count: "
with open(const.ROOT_DIR/"keys"/"api_uses.txt", 'r') as f:
	s = str(f.read())
	count = int(s[30:])
	count += 1
 
with open(const.ROOT_DIR/"keys"/"api_uses.txt", 'w') as f:	
	s = "Today's Google API use count: " + str(count)
	f.write(s)