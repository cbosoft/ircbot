#!/usr/bin/env python3




import datetime
import socket
import time
import ssl
import re
import random
import sys
import subprocess as sp


def runsh(command):
    pr = sp.Popen(command, shell=True, stdout=sp.PIPE)
    rv = pr.wait()
    stdout = pr.stdout.read().decode()
    return stdout


def send_command(server, command):
    bc = f'{command}\n'.encode()
    print(bc)
    server.send(bc)

def get_server(contect, *, nick, port, host, **kwargs):
    server = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host)
    server.connect((host, port))
    send_command(server, f'NICK {nick}\n')
    send_command(server, f'USER {nick} 0 * :bot\n')

    while True:
        s = server.recv(2048)
        print(s)
        s = s.decode().strip('\n\r')
        handle_message(server, s, **kwargs)
        if ENDMOTD_RE.match(s):
            break

    print('BOT HAS CONNECTED')
    return server


def join_channel(server, *, channel, **kwargs):
    send_command(server, f'JOIN {channel}\n')

    s = 'notblank'
    while True:
        s = server.recv(2048)
        print(s)
        s = s.decode().strip('\n\r')
        handle_message(server, s, channel=channel, **kwargs)
        if ENDJOIN_RE.match(s):
            break
    print(f'BOT HAS JOINED CHANNEL {channel}')

    
def send_message(server, message, channel, **kwargs):
    command = f'PRIVMSG {channel} {message}'
    send_command(server, command)

    
def handle_message(server, s, **kwargs):
    print(kwargs)
    if ERROR_RE.match(s):
        raise Exception(f'Something went wrong:\n{s}')
    elif PING_RE.match(s):
        send_command(server, s.replace('PING', 'PONG'))
    elif re.match(BOTCMD_re.format(**kwargs), s):
        botcommand = s.split(':!', 1)[1]
        handle_botcommand(server, botcommand, **kwargs)

def handle_botcommand(server, c, **kwargs):
    c = c.strip()
    if c in ['hi', 'hello', 'hey']:
        send_message(server, random.choice(greetings), **kwargs)
    elif c == 'fortune':
        fortune = runsh('fortune news')
        for line in fortune.split('\n'):
            send_message(server, line.replace('\t', '  '), **kwargs)













ERROR_RE = re.compile(r'^ERROR.*')
PING_RE = re.compile(r'^PING.*')
ENDMOTD_RE = re.compile(r'.*:End of /MOTD.*')
ENDJOIN_RE = re.compile(r'.*:End of /NAMES.*')
BOTCMD_re = r'.* {channel}.*:!.*'

context = ssl.SSLContext()
context.load_verify_locations('/home/chris/.irssi/server.cert.pem')


    
inputs = {
    'host'   : '130.159.42.114',
    'nick'     : 'bot',
    'channel'  : '#general',
    'port'     : 6697
}

if '--testing' in sys.argv:
    inputs['channel'] = '#testing'

greetings = [
    'IT\'s YA BOI; BOT',
    'HOLLA',
    'HI',
    'HELLO HUMAN',
    'WHAT ARE THE HAPPY HAPS?'
]

server = get_server(context, **inputs)
join_channel(server, **inputs)

send_message(server, random.choice(greetings), **inputs)
buf = str()
while True:
    
    try:
        buf += server.recv(2048).decode('utf-8')
    except UnicodeDecodeError:
        continue
    
    lines = buf.split('\n')
    buf = lines.pop()
    
    for line in lines:
        handle_message(server, line, **inputs)
