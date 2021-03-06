#!/usr/bin/env python3

import datetime
import socket
import time
import ssl
import re
import random
import sys
import os
import json
from collections import defaultdict

from ircbot.ircbot import IRCBot
from ircbot.runsh import runsh
from ircbot.server_status import get_server_status
from ircbot.search import search
from ircbot.show_help import show_help
from ircbot.fortune import fortune
from ircbot.info import about
from ircbot.phrases import send_phrase, greet, chastise, kw_coffee, kw_tea
from ircbot.goodbooks import read_goodbooks, show_goodbooks, dislike_user
from ircbot.afk import set_nick_afk, return_from_afk, check_afk
from ircbot.admin import seppuku, restart
from ircbot.log import log
from ircbot.test import run_tests
from ircbot.tumbleweed import tumbleweed


commands={
    'help': {
        'doc': '\'!help\' --- show this help message.', 
        'func': show_help
    },
    'fortune': {
        'doc': '\'fortune\' --- show a snippet of wisdom',
        'func': fortune
    },
    'hi': {
        'doc': '\'!hi\' --- say hello',
        'func': greet
    },
    'coffee': {
        'func': kw_coffee
    },
    'tea': {
        'func': kw_tea
    },
    'goodbooks': {
        'doc': '\'!goodbooks\' --- show info on what bot thinks of people',
        'func': show_goodbooks
    },
    'afk': {
        'doc': '\'!afk [<reason>]\' --- log self as afk, and optionally give a reason.',
        'func': set_nick_afk
    },
    'search': {
        'doc': '\'!search <query>\' --- search the internet',
        'func': search
    },
    'seppuku': {
        'func': seppuku
    },
    'restart': {
        'func': restart
    },
    'server': {
        'doc': '\'!server [all]\' --- poll the server for running processes',
        'func': get_server_status
    },
    'tumbleweed': {
        'doc': '\'!tumbleweed\' --- run some tumbleweed accross the chat',
        'func': tumbleweed
    },
    'about': {
        'doc': '\'!about\' --- get some information about the bot',
        'func': about
    }
}

bot = IRCBot(json_path='settings.json', commands=commands)
if '--testing' in sys.argv:
    bot.nick = 'PROTO_BOT'
bot.connect()
bot.join_channel('#general' if '--testing' not in sys.argv else '#testing')

if '--run-tests' in sys.argv:
    run_tests(bot)
else:
    bot.run()
