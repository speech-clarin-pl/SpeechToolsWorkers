import argparse
import logging
import os.path
from grp import getgrnam
from pwd import getpwnam

import daemon
from lockfile.pidlockfile import PIDLockFile

import config
import worker

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run worker program')
    parser.add_argument('--log', '-l', help='log to file instead of screen')
    parser.add_argument('--daemon', '-d', help='run as daemon', action='store_true')
    parser.add_argument('--pidfile', '-p', help='setup a pid lockfile of daemon (required!)')
    parser.add_argument('--user', '-u', help='set user of daemon')
    parser.add_argument('--group', '-g', help='set group of daemon')

    args = parser.parse_args()

    config.logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    keep_fds = None
    if args.log:
        handler = logging.FileHandler(args.log, 'a')
        keep_fds = [handler.stream.fileno()]
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    config.logger.addHandler(handler)

    chdir = os.path.dirname(os.path.realpath(__file__))

    if args.daemon:
        if not args.pidfile:
            print 'PID file is required for daemon mode!'
            exit(1)

        pid = PIDLockFile(os.path.realpath(args.pidfile))

        if args.user:
            uid = getpwnam(args.user)
        else:
            uid = os.getuid()
        if args.group:
            gid = getgrnam(args.group)
        else:
            gid = os.getgid()

        with daemon.DaemonContext(pidfile=pid, working_directory=chdir, files_preserve=keep_fds, uid=uid, gid=gid):
            worker.run()

    else:
        worker.run()
