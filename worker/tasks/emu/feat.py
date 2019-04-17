from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from typing import List


def send_commands(commands):
    p = Popen(['R', '--vanilla'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    p.stdin.write(commands.encode('utf-8'))
    p.stdin.close()
    p.stdout.readlines()


def run_feat(feat: List[str], wav: Path):
    dirpath = wav.parent
    if len(feat) == 0:
        return
    cmd_str = 'library("wrassp")\n'
    for cmd in feat:
        cmd_str += f'{cmd}("{wav}",outputDirectory="{dirpath}")\n'
    send_commands(cmd_str)
