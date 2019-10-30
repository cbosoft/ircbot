import json
from collections import defaultdict

def like_user(bot, nick):
    bot.esteem[nick] += 1
    write_goodbooks(bot)


def dislike_user(bot, nick):
    bot.esteem[nick] -= 1
    write_goodbooks(bot)


def write_goodbooks(bot):
    with open(bot.ESTEEM_FILE, 'w') as ef:
        json.dump(dict(**bot.esteem), ef)


def read_goodbooks(bot):
    try:
        with open(bot.ESTEEM_FILE) as ef:
            esteem = json.load(ef)
    except:
        esteem = dict()
    bot.esteem = defaultdict(int, **esteem)


def show_goodbooks(bot, *args):
    for user, level in bot.esteem.items():
        est = 'LIKE' if level > 0 else 'FEEL NEUTRALLY TOWARD' if level == 0 else 'DISLIKE'
        bot.send_msg(f'I {est} {user.upper()} ({level})')
