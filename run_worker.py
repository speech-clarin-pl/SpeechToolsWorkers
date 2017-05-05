import argparse
import logging
import os.path
import sys

import daemonize

import workers

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run worker program')
    parser.add_argument('worker', help='Name of worker to run. Examples: ffmpeg, normalization, speech')
    parser.add_argument('--daemon', '-d', help='run as daemon', action='store_true')
    parser.add_argument('--log', '-l', help='log to file')
    parser.add_argument('--pidfile', '-p', help='setup a pid lockfile')

    args = parser.parse_args()

    if args.log:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s',
                            filename=args.log,
                            filemode='a')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s')

    pidfile = None
    if args.pidfile:
        pidfile = args.pidfile

    if not args.worker in workers.workers:
        print 'Worker {} not found!'.format(args.worker)
        exit(1)

    action = workers.workers[args.worker]

    if args.daemon:
        d = daemonize.Daemonize(app=os.path.basename(sys.argv[0]), pid=pidfile, action=action)
        d.start()
    else:
        action()
