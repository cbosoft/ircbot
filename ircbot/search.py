import re
import requests
import time

from bs4 import BeautifulSoup as BS
import urllib.parse as urlparse
import random


DDG_URL = 'http://duckduckgo.com?q={}'


def search(bot, query, *args):
    cmd = f'search {query}'
    if cmd in bot.cache:
        if time.time() - bot.cache[cmd]['time'] < (60*60):
            bot.send_msg('OOH I HAVE LOOKED THIS UP BEFORE!')
            bot.send_msg('HERE IS WHAT I REMEMBER:')
            bot.send_msg(' ')
            bot.send_msg(bot.cache[cmd]['output'])

    bot.send_msg(f'OKAY {random.choice(bot.phrase_book["person"])}, I WILL SEARCH THAT FOR YOU.')
    resp = requests.get(DDG_URL.format(query), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})

    n = 3

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
            f'└ {snippet}',
            ' '
        ])
    rv = rv[:-1]
    bot.cache[cmd] = { 'time': time.time(), 'output': rv }
    bot.send_msg('RESULTS:')
    bot.send_msg(rv)
