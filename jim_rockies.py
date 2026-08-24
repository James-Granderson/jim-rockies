import urllib2
import config

url = "https://therundown.io/api/v2/sports/3/events/2026-08-22"

request = urllib2.Request(url)
request.add_header("X-TheRundown-Key", config.API_KEY)
request.add_header("User-Agent", "Mozilla/5.0")

response = urllib2.urlopen(request)

data = response.read()

open("mlb_data.json", "w").write(data)

print "Saved."
print "Characters:", len(data)
