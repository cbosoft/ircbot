from ircbot.runsh import runsh

def fortune(bot, *args):
    fortune = runsh('fortune news')
    bot.send_msg(fortune)

