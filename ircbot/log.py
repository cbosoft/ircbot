import os
import time


def get_logname():
    return os.path.expanduser(time.strftime('~/ircbot-log_%Y-%m-%d.txt'))


def log(bot, message):
    if not bot.logging:
        return

    now = time.strftime('%Y-%m-%d %H:%M:%S')

    with open(get_logname(), 'a') as f:
        f.write(f'{now} :: {message}\n')
