import re
import requests
from bs4 import BeautifulSoup as BS

DDG_URL = 'http://duckduckgo.com?q={}'

def search(query):
    resp = requests.get(DDG_URL.format(query), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
    
    if not resp:
        return None

    bs = BS(resp.content, features='lxml')
    for res in bs.find_all('div', attrs={'class':'result'}):
        pass
    #TODO: parese result div tags for url and name 

search('foo')
