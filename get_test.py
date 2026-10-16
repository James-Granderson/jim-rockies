"""Basic HTTP GET using the Python 3 standard library."""

from urllib.request import urlopen

with urlopen("https://example.com") as response:
    print(response.info())
    print(response)
    print(response.read())
