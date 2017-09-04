import argparse
import logging
import os.path
import sys

import daemonize

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

        d = daemonize.Daemonize(app=os.path.basename(sys.argv[0]), pid=args.pidfile, action=worker.run,
                                keep_fds=keep_fds,
                                user=args.user, group=args.group, chdir=chdir)
        d.start()
    else:
        worker.run()
