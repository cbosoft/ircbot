import subprocess as sp
from collections import defaultdict

from runsh import runsh

def get_server_status(ignored_users=['root', 'colord', 'uuidd', 'lp', 'syslog', 
    'message+', 'lightdm', 'rtkit', 'avahi', 'daemon', 'systemd+'],
        ignored_procs=[]#['sshd', 'systemd', '(sd-pam)']
        ):
    server_output = runsh("ssh chris@srv \"top -b -n 1\"")[:-1]
    user_commands = defaultdict(list)
    user_proc_cpu = defaultdict(lambda: defaultdict(float))
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
    
    avload = tot_cpu / ncpus
    m = [ [f'TOT. RAM: {tot_mem:.0f}%', f'CPU: {avload:.0f}%'], ['USER', '#PROCS', 'CPU', 'HIGHLIGHTS'] ]
    for user, procs in user_commands.items():
        proc_count = len(procs)
        unique_procs = list(set(procs))
        unique_procs = filter(lambda p: p not in ignored_procs , unique_procs)

        procs_and_counts = [(uniq, procs.count(uniq), user_proc_cpu[user][uniq]) for uniq in unique_procs]
        procs_and_counts = list(reversed(sorted(procs_and_counts, key=lambda r: r[2])))
        user_cpu = sum([pcc[2] for pcc in procs_and_counts])

        procs_and_counts = list(filter(lambda r: r[2] > 1.0, procs_and_counts))

        m.append([f'{user}', f'{len(procs)}', f'{user_cpu:.1f}%', ' ['])
        for proc, count, __ in procs_and_counts:
            if count > 1:
                m[-1][-1] += f'{count}×'
            m[-1][-1] += proc
            m[-1][-1] += ', '
        m[-1][-1] = m[-1][-1][:-2]

        if procs_and_counts:
            m[-1][-1] += '] '

        message = list()
        for row in m:
            mess = '|  '.join([r.ljust(15) for r in row])
            message.append(mess)

    return message

if __name__ == "__main__":
    for line in get_server_status():
        print(line)
