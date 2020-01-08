from time import sleep

def tumbleweed(bot, *args):
    l = 5
    m = 3
    for i in range(l):
        bot.send_msg(m*i*'_'+'@' + m*(l-i-1)*'_')
        sleep(1)
