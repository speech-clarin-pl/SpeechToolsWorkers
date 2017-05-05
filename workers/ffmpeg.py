import json
from workers import logger
import os
import os.path
from subprocess import call

import pika
from bson.objectid import ObjectId
from pymongo import MongoClient

client = MongoClient()


def update_db(id, fid, file):
    upd = {'$set': {'media.{}.file_path'.format(fid): file},
           '$unset': {'media.{}.error_converting'.format(fid): ''}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def update_db_error(id, fid):
    upd = {'$set': {'media.{}.error_converting'.format(fid): True}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def run():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='ffmpeg', durable=True)

    logger.info('FFMPEG queue waiting...')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        cmd = ['ffmpeg', '-i', data['input'], '-acodec', 'pcm_s16le', '-ac',
               '1', '-ar', '16k', data['output']]
        logger.info('Running: ' + ' '.join(cmd))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        try:
            with open(os.devnull, 'w') as n:
                call(cmd, stdin=n, stdout=n, stderr=n)
        except Exception as e:
            logger.error(e)
        if os.path.exists(data['output']):
            logger.info('Finished processing: ' + data['output'])
            update_db(data['id'], data['fid'], data['output'])
        else:
            logger.info('Error processing: ' + data['output'])
            update_db_error(data['id'], data['fid'])

    # if more than one worker:
    # channel.basic_qos(prefetch_count=1)

    channel.basic_consume(callback, queue='ffmpeg')
    channel.start_consuming()
