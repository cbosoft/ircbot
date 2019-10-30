import subprocess as sp

def runsh(command):
    pr = sp.Popen(command, shell=True, stdout=sp.PIPE)
    stdout = pr.stdout.read().decode()
    return stdout.replace('\t', '  ').split('\n')[:-1]
