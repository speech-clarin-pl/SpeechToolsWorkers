import os
from subprocess import Popen, PIPE, STDOUT


def make_archive(dir, archive):
    parent_dir = os.path.dirname(dir)
    dir_name = os.path.basename(dir)
    cmd = ['zip', '-r', archive, dir_name]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=parent_dir)
    p.stdin.close()
    for l in p.stdout.readlines():
        pass
