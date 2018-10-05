import os
from subprocess import Popen, PIPE, STDOUT


def send_commands(commands):
    p = Popen(['R', '--vanilla'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    p.stdin.write(commands.encode('utf-8'))
    p.stdin.close()
    for l in p.stdout.readlines():
        pass


def run_feat(feat, wav):
    dirpath = os.path.dirname(wav)
    if len(feat) == 0:
        return
    cmd_str = 'library("wrassp")\n'
    for cmd in feat:
        cmd_str += u'{}("{}",outputDirectory="{}")\n'.format(cmd, wav, dirpath)
    send_commands(cmd_str)
