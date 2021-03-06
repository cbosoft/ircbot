import time
import subprocess as sp
from collections import defaultdict
import random

from ircbot.runsh import runsh


def get_server_status(bot, rest_of_message, *args):
    show_all = rest_of_message == 'all'
    print(rest_of_message)
    cmd = "!server" if not show_all else "!server_all"
    if cmd in bot.cache:
        if time.time() - bot.cache[cmd]['time'] < 60:
            bot.send_msg('AHA! I HAVE SPOKEN TO MY FRIEND THE SERVER RECENTLY')
            bot.send_msg('I REMEMBER WHAT SHE SAID:')
            bot.send_msg(bot.cache[cmd]['output'])
            return

    bot.send_msg(f'OKAY {random.choice(bot.phrase_book["person"])}, I WILL CHECK ON MY FRIEND THE SERVER')
    time.sleep(1)
    bot.send_msg("HERE'S WHAT SHE SAID:")
    kwargs = dict()
    if show_all:
        kwargs['trunc_perc'] = -1.0

    try:
        server_status = _get_server_status(**kwargs)
    except Exception:
        bot.send_msg('SHE\'s NOT SPEAKING TO ME RIGHT NOW, #SADFACE')
        return 1
    bot.cache[cmd] = {'time': time.time(), 'output': server_status}
    bot.send_msg(server_status)
    return 0


def _get_server_status(
        ignored_users=['root', 'colord', 'uuidd', 'lp', 'syslog', 'message+', 'lightdm', 'rtkit', 'avahi', 'daemon', 'systemd+'],
        trunc_perc=0.5
        ):

    server_output = runsh("ssh chris@srv \"top -b -n 1\"")[:-1]
    user_commands = defaultdict(list)
    user_proc_cpu = defaultdict(lambda: defaultdict(float))
    user_proc_ram = defaultdict(lambda: defaultdict(float))
    tot_cpu = 0.0
    tot_mem = 0.0
    ncpus = 112
    for line in server_output[7:]:
        try:
            s = line.split()
            user = s[1]
            cpu = float(s[-4])
            mem = float(s[-3])
            cmd = s[-1]
        except:
            continue

        tot_cpu += cpu
        tot_mem += mem
        if user in ignored_users:
            continue
        user_commands[user].append(cmd)
        user_proc_cpu[user][cmd] += cpu/ncpus
        user_proc_ram[user][cmd] += mem
    
    avload = tot_cpu / ncpus
    table = [ 
        [f'TOT. RAM: {tot_mem:.0f}%', f'CPU: {avload:.0f}%'], 
        ['USER', '#PROCS', 'CPU', 'RAM', 'HIGHLIGHTS'] 
    ]
    for user, procs in user_commands.items():
        proc_count = len(procs)
        unique_procs = list(set(procs))

        proc_count_cpu = [(uniq, procs.count(uniq), user_proc_cpu[user][uniq], user_proc_ram[user][uniq]) for uniq in unique_procs]

        # sort processes in descending order by CPU usage
        proc_count_cpu = list(reversed(sorted(proc_count_cpu, key=lambda r: r[2])))

        # get total user CPU and RAM usage
        user_cpu = sum([pcc[2] for pcc in proc_count_cpu])
        user_ram = sum([pcc[3] for pcc in proc_count_cpu])

        # trim out small usage (\leq .5%) processes
        proc_count_cpu = list(filter(lambda r: r[2] > trunc_perc, proc_count_cpu))

        table.append([f'{user}', f'{len(procs)}', f'{user_cpu:.1f}%', f'{user_ram:.1f}%', ' ['])
        for proc, count, __, __ in proc_count_cpu:
            if count > 1:
                table[-1][-1] += f'{count}×'
            table[-1][-1] += proc
            table[-1][-1] += ', '
        table[-1][-1] = table[-1][-1][:-2]

        if proc_count_cpu:
            table[-1][-1] += '] '

    formatted_table = ['|  '.join([r.ljust(15) for r in row]) for row in table]
    return formatted_table


if __name__ == "__main__":
    for line in _get_server_status():
        print(line)
