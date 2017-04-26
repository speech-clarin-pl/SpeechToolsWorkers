import pika
import daemon
import daemon.pidfile
import json
from subprocess import Popen, STDOUT
import logging
import argparse
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import os
import os.path

client = MongoClient()

pat = re.compile('[^\w\s]', flags=re.U)
num = re.compile('[0-9]', flags=re.U)
ws = re.compile('\s+', flags=re.U)


def check_files(dir, files):
    for file in files:
        if not os.path.exists(dir + '/' + file):
            return False
    return True


def align(type, wav_file, txt_file, output):
    cmd = ['bash', './speech_tools/{}/run.sh'.format(type), wav_file, txt_file, output]
    with open(output + '.log', 'w') as log:
        logging.info('Running {}'.format(' '.join(cmd)))
        proc = Popen(cmd, stdout=log, stderr=STDOUT)
        ret = proc.wait()
    if ret != 0:
        return None
    files = ['words.ctm', 'phonemes.ctm', 'segmentation.TextGrid', 'emuDB']
    if check_files(output, files):
        return files
    else:
        return None


def run_task(type, id):
    project = get_files_db(id)
    if type == 'forcealign':
        wav_file = project['media']['default']['file_path']
        txt_file = project['media']['default']['trans_file_path']
        output = project['path'] + '/forcealign'
        return align('ForcedAlign', wav_file, txt_file, output)
    elif type == 'segmentalign':
        wav_file = project['media']['default']['file_path']
        txt_file = project['media']['default']['trans_file_path']
        output = project['path'] + '/segmentalign'
        return align('SegmentAlign', wav_file, txt_file, output)
    else:
        raise RuntimeError('unknown task type')


def get_files_db(id):
    project = client.clarin.projects.find_one({'_id': ObjectId(id)})
    return project


def update_db(id, type, formats):
    upd = {'$set': {'tools.{}.files'.format(type): formats},
           '$unset': {'tools.{}.error'.format(type): ''}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def update_db_error(id, type, desc):
    upd = {'$set': {'tools.{}.error'.format(type): desc}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def run_program():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='speech_tools', durable=True)

    logging.info('Speech tools queue waiting...')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info('Running {} for {} '.format(data['task'], data['id']))
        try:
            ret = run_task(data['task'], data['id'])
            if ret and len(ret) > 0:
                update_db(data['id'], data['task'], ret)
            else:
                update_db_error(data['id'], data['task'], 'task finished unsuccesfully')
        except RuntimeError as e:
            update_db_error(data['id'], data['task'], str(e))
        logging.info('Done')

    # if more than one worker:
    # channel.basic_qos(prefetch_count=1)

    channel.basic_consume(callback, queue='speech_tools')
    channel.start_consuming()


def daemon_run(pidfile):
    with daemon.DaemonContext(pidfile=pidfile):
        run_program()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speech tools worker queue')
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
