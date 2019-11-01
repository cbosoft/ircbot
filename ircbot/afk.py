import datetime

def set_nick_afk(bot, reason, nick, *args):
    '''Set nick as being away, log time this happened'''
    t = datetime.datetime.now().strftime("%m-%d, %H:%M:%S")
    bot.afk_users[nick] = {
            'timestamp': t,
            'messages' : [],
            'reason'   : reason
        }
    bot.send_msg(f'{nick} is now AFK because "{reason}".')
    # TODO: save AFK status to file


def return_from_afk(bot, nick):
    '''Unset nick as AFK: read out missed messages'''

    s = f'Welcome back {nick}, while you were away '

    # TODO walrus-ify when 3.8 is in arch repo
    if bot.afk_users[nick]['messages']:
        n_msg = len(bot.afk_users[nick]['messages'])
        s += f'you received {n_msg} messages:'
        bot.send_msg(s, to=nick)
        for m in bot.afk_users[nick]['messages']:
            bot.send_msg(m, to=nick)
    else :
        s += f'nobody messaged you, feels bad :('
        bot.send_msg(s, to=nick)

    del bot.afk_users[nick]
    # TODO: save AFK status to file


def check_afk(bot, from_nick, to_nick, message):
    '''
    User can say he/she is AFK, when someone tags a user bot checks
    whether or not user is AFK (in dict). If True then saves message
    for when user returns
    '''

    if to_nick not in bot.afk_users:
        return
    
    since = bot.afk_users[to_nick]["timestamp"]
    reason = bot.afk_users[to_nick]["reason"]
    msg = f'@{from_nick.upper()}, {to_nick.upper()} HAS BEEN AFK SINCE {since}'
    if reason: msg += ' because {reason}'
    msg += '. I WILL RELAY YOUR MESSAGE WHEN THEY RETURN.'
    bot.send_msg(msg)
    t = datetime.datetime.now().strftime("%m-%d, %H:%M:%S")
    savemsg = f'{t} {from_nick}: {message}'
    bot.afk_users[to_nick]['messages'].append(savemsg)
