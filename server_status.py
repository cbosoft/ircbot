import subprocess as sp
from collections import defaultdict

from runsh import runsh

def get_server_status(
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

        table.append([f'{user}', f'{len(procs)}', f'{user_cpu:.1f}%', f'{user_ram:.1f}', ' ['])
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
    for line in get_server_status():
        print(line)
