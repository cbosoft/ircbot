#!/usr/bin/env python3

import datetime
import socket
import time
import ssl
import re
import random
import sys
import subprocess as sp
import os
import json
from collections import defaultdict

def runsh(command):
    pr = sp.Popen(command, shell=True, stdout=sp.PIPE)
    pr.wait()
    stdout = pr.stdout.read().decode()
    return stdout.replace('\t', '  ').split('\n')

class IRCBot:

    ERROR_RE = re.compile(r'^ERROR.*')
    PING_RE = re.compile(r'^PING.*')
    ENDMOTD_RE = re.compile(r'.*:End of /MOTD.*')
    ENDJOIN_RE = re.compile(r'.*:End of /NAMES.*')
    MESSAGE_RE = re.compile(r'^:(.*)!.*:(.*)')
    TAGGED_RE = re.compile(r'.*@([!\w]*).*')

    SOURCE = 'https://github.com/cbosoft/ircbot'
    OPERCERT = '.operator.cert'
    PHRASE_BOOK_DIR = './phrase_book'

    phrase_book = dict()
    afk_users   = dict()
    esteem = defaultdict(int)

    def __init__(self, *, nick='CPE_Bot', port=None, host=None, server_cert_location=None):
        self.nick = nick
        self.port = port
        self.host = host
        self.server_cert_location = server_cert_location
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
        self.greet()

        
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

    def send_phrase(self, phrase_type):
        if phrase_type not in self.phrase_book:
            return '...'

        self.send_msg(random.choice(self.phrase_book[phrase_type]))


    def greet(self):
        '''Choose a greeting from the self.GREETINGS list, and message the channel'''
        time.sleep(random.random()*0.5)
        self.send_phrase('greetings')


    def chastise(self):
        '''Chastise the user for wrong-doing'''
        self.send_phrase('chastisations')


    def kick(self, nick):
        '''Kick someone from server'''
        self.send_cmd(f'KICK {nick}')
        
    def command_go_afk(self, nick):
        t = datetime.datetime.now().strftime("%m-%d, %H:%M:%S")
        self.afk_users[nick] = {'timestamp':t,
                                'messages':[]}
        self.send_message(f'{nick} is now AFK.')
        
    def return_from_afk(self,nick):
        s = f'Welcome back {nick}, while you were away '
        # here is where the walrus operator would be good
        # if n_msg := len(afk_users[nick]['messages']:
        if afk_users[nick]['messages']:
            n_msg = len(afk_users[nick]['messages'])
            s += f'you received {n_msg} messages:'
            self.send_message(s)
            for m in afk_users[nick]['messages']:
                self.send_message(m)
        else :
            s += f'nobody messaged you, feels bad :('
            self.send_message(s)
        del self.afk_users[nick]
        
    def check_afk(self,nick):
        '''
        User can say he/she is AFK, when someone tags a user bot checks
        whether or not user is AFK (in dict). If True then saves message
        for when user returns
        '''
        for afk_u in afk_users:
            if f'@{afk_u}' in message_string:
                # f strings don't work with \ break in the line
                msg = '@{}, {} has been AFK since {}. I will tell him'\
                      'your message when he returns.'.format(
                          user_from, afk_u, afk_users[afk_u]['timestamp'])
                self.send_msg(msg)
                t = datetime.datetime.now().strftime("%m-%d, %H:%M:%S")
                savemsg = f'{t} {user_from}: {message_string}'
                self.afk_users[afk_u]['messages'].append(savemsg)
    
    def like_user(self, nick):
        self.esteem[nick] += 1


    def dislike_user(self, nick):
        self.esteem[nick] -= 1


    def handle_message(self, s):
        '''
        In running the bot, input is monitored from users for a command or
        keyword. 
        '''

        s = s.strip()

        print(s)
        
        if self.ERROR_RE.match(s):
            raise Exception(f'Something went wrong:\n{s}')
        
        if self.PING_RE.match(s):
            self.send_cmd(s.replace('PING', 'PONG'))
            return
        
        mobj = self.MESSAGE_RE.match(s)

        if not mobj:
            return

        from_nick, message = mobj.groups()

        print(f'{self} RECEIVED MESSAGE: {message} FROM {from_nick}')

        if message.startswith('!'):
            self.handle_botcommand(message[1:], from_nick)

        for keyword in self.KEYWORDS:
            if keyword in message.lower():
                self.handle_botcommand(keyword, from_nick)

        mobj = self.TAGGED_RE.match(s)
        if mobj:
            to_nick = mobj.group(1)
            self.check_afk(from_nick, to_nick, message)

        if from_nick in self.afk_users and not '!afk' in message:
            self.return_from_afk(from_nick)


    def show_goodbooksbadbooks(self):
        for user, level in self.esteem.items():
            est = 'LIKE' if level > 0 else 'FEEL NEUTRALLY TOWARD' if level == 0 else 'DISLIKE'
            self.send_msg(f'I {est} {user.upper()} ({level})')


    def handle_botcommand(self, command, from_nick):

        self.esteem[from_nick]

        if command in ['hi', 'hello', 'hey']:
            self.greet()
        elif command == 'fortune':
            fortune = runsh('fortune news')
            self.send_msg(fortune)
        elif command == 'about':
            about = [
                '<!-- ircbot -->', 
                f'see github for source: {self.SOURCE}'
            ]
            self.send_msg(about)
        elif command == 'help':
            message = [
                'HELP HUMAN? OK.',
                'Commands:',
                '\'!hello\' -- bot will respond with greeting',
                '\'!fortune\' -- bot will respond with a message/quote',
                '\'!about\' -- bot will give some meta info about itself',
                '\'!goodbooks\' -- bot will tell you how it feels about users it has interacted with',
                '\'!help\' -- show this help'
            ]
            self.send_msg(message)
        elif command.lower() == 'coffee':
            self.like_user(from_nick)
            self.send_phrase('coffee')
        elif command.lower() == 'tea':
            self.dislike_user(from_nick)
            self.send_phrase('tea')
        elif command.lower() == 'goodbooks':
            self.show_goodbooksbadbooks()
        elif command.lower() == 'afk':
            self.command_go_afk(from_nick)
        else:
            self.dislike_user(from_nick)
            self.chastise()

    def log(self, message):
        pass # TODO

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
                self.log(line)
                self.handle_message(line)

            
bot = IRCBot(host='130.159.42.114', port=6697, server_cert_location='/home/chris/.irssi/server.cert.pem')
bot.connect()
bot.join_channel('#general' if '--testing' not in sys.argv else '#testing')
bot.run()
