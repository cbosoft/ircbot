def show_help(bot, command, from_nick, username, host, channel):
    bot.send_msg('YOU WANT HELP? OK:')
    for cmd_str, data in bot.commands.items():
        if 'doc' in data:
            bot.send_msg(data['doc'])
    return 0
