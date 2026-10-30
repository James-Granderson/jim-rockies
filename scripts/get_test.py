#python get_test.py
"""
This program demonstrates
a basic HTTP GET request.
"""

import urllib.request


with urllib.request.urlopen("https://example.com") as response:
    print(response.info())
    print(response)
    data = response.read()
    print(data)