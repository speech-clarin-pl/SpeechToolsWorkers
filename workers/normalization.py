import codecs
import json
import logging
import os
import os.path
import re

import pika
from bson.objectid import ObjectId
from pymongo import MongoClient

client = MongoClient()

pat = re.compile('[^\w\s]', flags=re.U)
num = re.compile('[0-9]', flags=re.U)
ws = re.compile('\s+', flags=re.U)


def normalize(input, output):
    with codecs.open(input, encoding='utf8') as fin:
        with codecs.open(output, 'w', encoding='utf8') as fout:
            for line in fin:
                line = line.lower()
                line = pat.sub(' ', line)
                line = num.sub(' ', line)
                line = ws.sub(' ', line)
                fout.write(line)


def update_db(id, fid, file):
    upd = {'$set': {'media.{}.trans_file_path'.format(fid): file},
           '$unset': {'media.{}.error_converting_trans'.format(fid): ''}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def update_db_error(id, fid):
    upd = {'$set': {'media.{}.error_converting_trans'.format(fid): True}}
    client.clarin.projects.update_one({'_id': ObjectId(id)}, upd)


def run():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='text_normalizer', durable=True)

    logging.info('Text normalization queue waiting...')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        try:
            normalize(data['input'], data['output']);
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

    channel.basic_consume(callback, queue='text_normalizer')
    channel.start_consuming()
