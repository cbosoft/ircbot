import subprocess as sp
from collections import defaultdict

from runsh import runsh

def get_server_status(ignored_users=['root', 'colord', 'uuidd', 'lp', 'syslog', 
    'message+', 'lightdm', 'rtkit', 'avahi', 'daemon', 'systemd+'],
        ignored_procs=['sshd', 'systemd', '(sd-pam)']
        ):
    server_output = runsh("ssh chris@srv \"top -b -n 1\"")[:-1]
    user_commands = defaultdict(list)
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
    
    avload = tot_cpu / ncpus
    m = [f'Av. CPU: {avload:.0f}%, TOT. RAM: {tot_mem:.0f}%']
    for user, procs in user_commands.items():
        proc_count = len(procs)
        unique_procs = list(set(procs))
        m.append(f'  {user} ({len(procs)}:')
        for i, uniq in enumerate(unique_procs):
            if uniq in ignored_procs:
                continue
            # TODO: walrus-ify
            ucount = procs.count(uniq)
            if ucount > 1:
                m[-1] += f' {ucount}*'
            m[-1] += uniq
            m[-1] += ', '
        m[-1] = m[-1][:-2]
        m[-1] += ') '
    return m
