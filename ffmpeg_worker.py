import pika
import daemon
import daemon.pidfile
import json
import os
import os.path
from subprocess import call
import logging
import argparse
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()


def update_db(id, fid, file):
    upd = {'$set': {'media.{}.file_path'.format(fid): file},
           '$unset': {'media.{}.error_converting'.format(fid): ''}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def update_db_error(id, fid):
    upd = {'$set': {'media.{}.error_converting'.format(fid): True}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def run_program():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='ffmpeg', durable=True)

    logging.info('FFMPEG queue waiting...')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        cmd = ['ffmpeg', '-i', data['input'], '-acodec', 'pcm_s16le', '-ac',
               '1', '-ar', '16k', data['output']]
        logging.info('Running: ' + ' '.join(cmd))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        try:
            with open(os.devnull, 'w') as n:
                call(cmd, stdin=n, stdout=n, stderr=n)
        except Exception as e:
            logging.error(e)
        if os.path.exists(data['output']):
            logging.info('Finished processing: ' + data['output'])
            update_db(data['id'], data['fid'], data['output'])
        else:
            logging.info('Error processing: ' + data['output'])
            update_db_error(data['id'], data['fid'])

    # if more than one worker:
    # channel.basic_qos(prefetch_count=1)

    channel.basic_consume(callback, queue='ffmpeg')
    channel.start_consuming()


def daemon_run(pidfile):
    with daemon.DaemonContext(pidfile=pidfile):
        run_program()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FFMPEG worker queue')
    parser.add_argument('--daemon', '-d', help='run as daemon', action='store_true')
    parser.add_argument('--log', '-l', help='log to file')
    parser.add_argument('--pidfile', '-p', help='setup a pid lockfile')

    args = parser.parse_args()

    if args.log:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s',
                            filename=args.log,
                            filemode='w')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s')

    pidfile = None
    if args.pidfile:
        pidfile = daemon.pidfile.TimeoutPIDLockFile(args.pidfile)

    if args.daemon:
        daemon_run(pidfile)
    else:
        run_program()
