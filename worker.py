import datetime
import hashlib
import json
import os

from bson import ObjectId

from config import logger
from tasks import text, audio, speech


def file_hash(filename):
    h = hashlib.sha1()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def files_hash(filenames):
    h = hashlib.sha1()
    for filename in filenames:
        with open(filename, 'rb', buffering=0) as f:
            for b in iter(lambda: f.read(128 * 1024), b''):
                h.update(b)
    return h.hexdigest()


def run():
    import pika
    from pymongo import MongoClient

    db = MongoClient()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='workers', durable=True)

    def get_file(file_id):
        input_res = db.clarin.resources.find_one({'_id': ObjectId(file_id)})
        return input_res['file']

    logger.info('Worker queue waiting...')

    def callback(ch, method, properties, body):

        ch.basic_ack(delivery_tag=method.delivery_tag)
        data = json.loads(body)

        try:
            task = data['task']
            logger.info('Performing {}...'.format(task))

            if task == 'text_normalize':
                output_name = text.normalize(data['work_dir'], get_file(data['input']))
            elif task == 'ffmpeg':
                output_name = audio.ffmpeg(data['work_dir'], get_file(data['input']))
            elif task == 'forcealign':
                output_name = speech.forcealign(data['work_dir'], get_file(data['audio']), get_file(data['transcript']))
            elif task == 'segmentalign':
                output_name = speech.segmentalign(data['work_dir'], get_file(data['audio']),
                                                  get_file(data['transcript']))
            elif task == 'recognize':
                output_name = speech.recognize(data['work_dir'], get_file(data['input']))
            else:
                raise RuntimeError('unknown task: ' + task)

            output_file = os.path.join(data['work_dir'], output_name)

            hash = file_hash(output_file)
            file = db.clarin.resources.find_one({'hash': hash})
            if file:
                os.remove(output_file)
                output_name = file['file']

            upd = {
                '$set': {'file': output_name, 'modified': datetime.datetime.utcnow(), 'hash': hash}}
            db.clarin.resources.update_one({'_id': ObjectId(data['output'])}, upd)

        except RuntimeError as e:
            logger.warn('Got error: ' + str(e))
            upd = {'$set': {'modified': datetime.datetime.utcnow(), 'error': str(e)}}
            db.clarin.resources.update_one({'_id': ObjectId(data['output'])}, upd)

    # if more than one worker:
    # channel.basic_qos(prefetch_count=1)

    channel.basic_consume(callback, queue='workers')
    try:
        channel.start_consuming()
    except:
        logger.exception('channel')
