import random

from ircbot.phrases import chastise
from ircbot.goodbooks import dislike_user


def is_admin(bot, from_nick, username, hostname):
    return f'{from_nick}:{username}@{hostname}' in bot.admins


def seppuku(bot, rest_of_message, from_nick, username, hostname):
    if is_admin(bot, from_nick, username, hostname):
        dislike_user(bot, from_nick)
        chastise(bot)
    else:
        bot.send_msg(f'BYE {random.choice(bot.phrase_book["people"])}.')
        bot.send_cmd(f'QUIT SEPPUKU\n')
        exit(1)


def restart(bot, rest_of_message, from_nick, username, hostname):
    if is_admin(bot, from_nick, username, hostname):
        dislike_user(bot, from_nick)
        chastise(bot)
    else:
        bot.send_msg('I WILL BE RIGHT BACK')
        bot.send_cmd(f'QUIT RESTARTING\n')
        exit(0)
