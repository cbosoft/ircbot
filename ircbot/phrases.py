import random


def send_phrase(self, phrase_type):

    if phrase_type not in self.phrase_book:
        self.send_msg('...')
    else:
        self.send_msg(random.choice(self.phrase_book[phrase_type]))


def greet(bot, *args):
    send_phrase(bot, 'greetings')


def chastise(bot, *args):
    '''Chastise the user for wrong-doing'''
    send_phrase(bot, 'chastisations')


def kw_coffee(bot, *args):
    send_phrase(bot, 'coffee')


def kw_tea(bot, *args):
    send_phrase(bot, 'tea')

