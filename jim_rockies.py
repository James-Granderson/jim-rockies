import urllib2
import config
#python jim_rockies.py

url = "PUT_THE_RUNDOWN_ENDPOINT_HERE"

url = url + "?api_key=" + config.API_KEY

response = urllib2.urlopen(url)

data = response.read()

print data
