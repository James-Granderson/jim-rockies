#python get_test.py
"""
This program demonstrates
a basic HTTP GET request.
"""

import urllib2


response = urllib2.urlopen("https://example.com")


print response.info()
print response

data = response.read()

print data