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




class IRCBot:

    ERROR_RE = re.compile(r'^ERROR.*')
    PING_RE = re.compile(r'^PING.*')
    ENDMOTD_RE = re.compile(r'.*:End of /MOTD.*')
    ENDJOIN_RE = re.compile(r'.*:End of /NAMES.*')
    MESSAGE_RE = re.compile(r'^:(.+)!(.+)@(.+) PRIVMSG #(.+) :(.+)')
    TAGGED_RE = re.compile(r'.*@([!\w]*).*')

    SOURCE = 'https://github.com/cbosoft/ircbot'
    OPERCERT = '.operator.cert'
    PHRASE_BOOK_DIR = './phrase_book'
    ESTEEM_FILE = os.path.expanduser('~/.ircbot_esteem.json')
    KEYWORDS = ['coffee', 'tea']

    phrase_book = dict()
    afk_users   = dict()
    esteem = defaultdict(int)
    error = None

    cache = dict()

    def __init__(self, *, 
            nick='CPE_Bot', 
            port=None, 
            host=None, 
            server_cert_location=None, 
            logging=True, 
            admins=[], 
            json_path=None, 
            commands=None):

        assert (port and host and server_cert_location) or json_path

        self.nick = nick
        self.port = port
        self.host = host
        self.server_cert_location = server_cert_location
        self.logging = logging
        self.admins = admins
        if json_path:
            with open(json_path) as fp:
                json_settings = json.load(fp)
            safe_get = lambda k, d: json_settings[k] if k in json_settings else d
            self.nick = safe_get('nick', self.nick)
            self.port = safe_get('port', self.port)
            self.host = safe_get('host', self.host)
            self.server_cert_location = safe_get('server_cert_location', self.server_cert_location)
            self.logging = safe_get('logging', self.logging)
            self.admins = safe_get('admins', self.admins)

        self.sock = 0
        self.channel = None

        if os.path.isfile(self.OPERCERT):
            with open(self.OPERCERT) as opcert:
                self.operator_cert = json.load(opcert)
        else:
            self.operator_cert = None

        if os.path.isdir(self.PHRASE_BOOK_DIR):
            phrase_files = os.listdir(self.PHRASE_BOOK_DIR)
            for phrase_file in phrase_files:
                phrase_type = phrase_file.replace('.txt', '')
                with open(f'{self.PHRASE_BOOK_DIR}/{phrase_file}') as phf:
                    phrases = phf.readlines()
                self.phrase_book[phrase_type] = [phrase.strip() for phrase in phrases]
        else:
            print(f'{self} COULD NOT FIND PHRASEBOOK {self.PHRASE_BOOK_DIR}')

        read_goodbooks(self)

        self.commands = commands
        print(commands)

    def __repr__(self):
        return f'IRCBot(nick={self.nick}, port={self.port}, host={self.host})'


    def connect(self):
        '''Connect to IRC server'''
        print(f'{self} IS CONNECTING...')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.server_cert_location:
            print(f'{self} USING SSL')
            self.sslcontext = ssl.SSLContext()
            self.sslcontext.load_verify_locations(self.server_cert_location)
            self.sock = self.sslcontext.wrap_socket(self.sock, server_hostname=self.host)

        self.sock.connect((self.host, self.port))
        self.send_cmd(f'NICK {self.nick}\n')
        self.send_cmd(f'USER {self.nick} 0 * :bot\n')

        while True:
            s = self.sock.recv(2048)
            s = s.decode().strip('\n\r')
            self.handle_message(s)
            if self.ENDMOTD_RE.match(s):
                break
            
        print(f'{self} HAS CONNECTED')

        if self.operator_cert:
            self.send_cmd(f"OPER {self.operator_cert['username']} {self.operator_cert['password']}")


    def get_props(self):
        rv = dict()
        rv['channel'] = self.channel
        rv['host'] = self.host
        rv['port'] = self.port
        return rv


    def join_channel(self, channel):
        print(f'{self} IS JOINING CHANNEL {channel}...')
        self.channel = channel
        self.send_cmd(f'JOIN {channel}\n')

        s = 'notblank'
        while True:
            s = self.sock.recv(2048)
            s = s.decode().strip('\n\r')
            self.handle_message(s)
            if self.ENDJOIN_RE.match(s):
                break
            
        print(f'{self} HAS JOINED CHANNEL {channel}')
        greet(self)


    def send_cmd(self, command):
        '''Send command to server'''
        
        if command[-1] != '\n':
            command += '\n'
        self.sock.send(command.encode())


    def send_msg(self, msg, to=None):
        '''Send message to server; send sequentially if message is a list'''
        
        if to is None:
            to = self.channel

        print(f'{self} IS SENDING A MESSAGE TO {to}: \'{msg}\'')

        if isinstance(msg, list):
            for line in msg:
                self.send_msg(line, to)
            return
        
        self.send_cmd(f'PRIVMSG {to} {msg}')


    def handle_message(self, s):
        '''
        In running the bot, input is monitored from users for a command or
        keyword. 
        '''

        s = s.strip()

        print(f'Handling message: {s}')
        
        if self.ERROR_RE.match(s):
            raise Exception(f'Something went wrong:\n{s}')
        
        if self.PING_RE.match(s):
            self.send_cmd(s.replace('PING', 'PONG'))
            return 0
        
        mobj = self.MESSAGE_RE.match(s)

        if not mobj:
            print('non-matching string')
            return 0

        groups = mobj.groups()
        user_info = groups[:-1]
        message = groups[-1]
        from_nick = user_info[0]

        print(f'{self} RECEIVED MESSAGE: {message} FROM {from_nick}')

        if message.startswith('!'):
            command = message[1:].lower()

            if ' ' in command:
                command, rest_of_message = command.split(' ', 1)
            else:
                rest_of_message = None

            self.handle_botcommand(command, rest_of_message, *user_info)

        for keyword in self.KEYWORDS:
            if keyword in re.split('[^\w]', message.lower()):
                self.handle_botcommand(keyword, None, *user_info)

        mobj = self.TAGGED_RE.match(s)
        if mobj:
            to_nick = mobj.group(1)
            check_afk(self, from_nick, to_nick, message)

        if from_nick in self.afk_users and not '!afk' in message:
            return_from_afk(self, from_nick)


    def is_admin(self, from_nick, username, host):
        return f'{from_nick}:{username}@{host}' in self.admins


    def handle_botcommand(self, command, rest_of_message, from_nick, *args):

        self.esteem[from_nick]

        if self.commands and command in self.commands:
            try:
                rv = self.commands[command]['func'](self, rest_of_message, from_nick, *args)
            except Exception as e:
                self.error = e
                rv = 1
        else:
            dislike_user(self, from_nick)
            chastise(self)
            rv = 0
        return rv


    def run(self):
        buf = str()
        while True:
            try:
                buf += self.sock.recv(2048).decode('utf-8')
            except UnicodeDecodeError:
                continue
    
            lines = buf.split('\n')
            buf = lines.pop()
    
            for line in lines:
                log(self, line)
                try:
                    self.handle_message(line)
                except Exception as e:
                    print(e)
                    send_phrase(self, 'error')
