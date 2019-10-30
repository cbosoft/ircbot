import re
import requests
from bs4 import BeautifulSoup as BS
import urllib.parse as urlparse

DDG_URL = 'http://duckduckgo.com?q={}'

def search(query, n=3):
    resp = requests.get(DDG_URL.format(query), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
    
    if not resp:
        return None

    rv = list()
    bs = BS(resp.content, features='lxml')
    for i, res in enumerate(bs.find_all('div', attrs={'class':'result'})):

        if i > (n-1):
            break

        title = res.find(attrs={'class':'result__title'}).getText().strip()
        link = urlparse.unquote(res.find(attrs={'class':'result__url'}).attrs['href'])
        snippet = res.find(attrs={'class':'result__snippet'}).getText().strip()

        link = link[link.index('http'):]

        rv.extend([
            f'┌ {title} ({link})',
            f'└ {snippet}'
        ])
        if i < n:
            rv.append(' ')
    return rv


if __name__ == "__main__":
    results = search('foo')

    for line in results:
        print(line)
