import datetime
import hashlib
import json
import time
from pathlib import Path

from bson import ObjectId

from worker.config import logger
from worker.tasks import text, audio, speech, emu


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
    while True:
        import pika
        from pymongo import MongoClient

        db = MongoClient()
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='workers', durable=True)

        def get_file(file_id):
            input_res = db.clarin.resources.find_one({'_id': ObjectId(file_id)})
            if not input_res or not input_res['file']:
                raise RuntimeError('File resource not found!')
            return input_res['file']

        logger.info('Worker queue waiting...')

        def callback(ch, method, properties, body):

            ch.basic_ack(delivery_tag=method.delivery_tag)
            data = json.loads(body)

            try:
                task = data['task']
                logger.info(u'Performing {}...'.format(task))

                work_dir = Path(data['work_dir'])

                if task == 'text_normalize':
                    output_file = text.normalize(work_dir, get_file(data['input']))
                elif task == 'ffmpeg':
                    output_file = audio.ffmpeg(work_dir, get_file(data['input']))
                elif task == 'forcealign':
                    output_file = speech.forcealign(work_dir, get_file(data['audio']),
                                                    get_file(data['transcript']))
                elif task == 'segmentalign':
                    output_file = speech.segmentalign(work_dir, get_file(data['audio']),
                                                      get_file(data['transcript']))
                elif task == 'recognize':
                    output_file = speech.recognize(work_dir, get_file(data['input']))
                elif task == 'diarize':
                    output_file = speech.diarize(work_dir, get_file(data['input']))
                elif task == 'vad':
                    output_file = speech.vad(work_dir, get_file(data['input']))
                elif task == 'kws':
                    output_file = speech.kws(work_dir, get_file(data['audio']), get_file(data['keywords']))
                elif task == 'emupackage':
                    output_file = emu.task.package(work_dir, data['project'], db)
                else:
                    raise RuntimeError('unknown task: ' + task)

                hash = file_hash(output_file)
                file = db.clarin.resources.find_one({'hash': hash})
                if file:
                    output_file.unlink()
                    output_file = work_dir / file['file']

                upd = {
                    '$set': {'file': str(output_file.relative_to(work_dir)), 'modified': datetime.datetime.utcnow(),
                             'hash': hash}}
                db.clarin.resources.update_one({'_id': ObjectId(data['output'])}, upd)

            except RuntimeError as e:
                logger.warn('Got error: ' + str(e))
                upd = {'$set': {'modified': datetime.datetime.utcnow(), 'error': str(e)}}
                db.clarin.resources.update_one({'_id': ObjectId(data['output'])}, upd)

        # if more than one worker:
        # channel.basic_qos(prefetch_count=1)

        channel.basic_consume(on_message_callback=callback, queue='workers')
        try:
            channel.start_consuming()
        except:
            logger.exception('channel')
            time.sleep(3)
