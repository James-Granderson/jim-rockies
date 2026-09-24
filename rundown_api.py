import urllib.request
import config
#python jim_rockies.py

url = "PUT_THE_RUNDOWN_ENDPOINT_HERE"

url = url + "?api_key=" + config.API_KEY

with urllib.request.urlopen(url) as response:
    data = response.read()

print(data)
