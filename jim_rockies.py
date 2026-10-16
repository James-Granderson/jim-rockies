from urllib.parse import urlencode
from urllib.request import urlopen

import config


def build_url():
    url = config.ENDPOINT
    if config.API_KEY:
        separator = "&" if "?" in url else "?"
        url = url + separator + urlencode({"api_key": config.API_KEY})
    return url


def fetch_market(url):
    with urlopen(url) as response:
        return response.read()


def main():
    url = build_url()
    if "PUT_THE_RUNDOWN_ENDPOINT_HERE" in url:
        print("Set RUNDOWN_ENDPOINT and RUNDOWN_API_KEY before fetching live data.")
        return
    print(fetch_market(url))


if __name__ == "__main__":
    main()
