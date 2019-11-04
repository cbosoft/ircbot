import time

from ircbot.colours import *

TESTS = [
        # incomplete input: commands that have not bee properly or fully received
        ('incomplete input 1', ''),
        ('incomplete input 2', 'partial'),
        ('incomplete input 3', ':nick!@garble'),
        ('incomplete input 4', ':nick!user@garble'),
        ('incomplete input 4', ':nick!user@garble PRIVMSG #channel')
]

# command input: commands sent to server with and without argument
for i, command in enumerate(['afk', 'help', 'hi', 'search', 'server', 'goodbooks', 'fortune']):
    TESTS.append(
            (f'command (-arg) {i+1}', f':nick!user@host PRIVMSG #testing :!{command}') )
    TESTS.append(
            (f'command (+arg) {i+1}', f':nick!user@host PRIVMSG #testing :!{command} something') )


def run_tests(bot):
    for testname, testmsg in TESTS:
        print(f'{BOLD}{testname}{RESET}')
        if bot.handle_message(testmsg):
            print(f'{BOLD}{BG_RED}{FG_WHITE}FAILED{RESET}')
            return
        else:
            print(f'{BOLD}{FG_GREEN}PASSED{RESET}')
        time.sleep(30)
