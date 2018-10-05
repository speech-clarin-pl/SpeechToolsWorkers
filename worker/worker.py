import json

import pika

from worker.config import logger, work_dir
from worker.tasks import text, audio, speech

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='workers', durable=True)
channel.queue_declare(queue='worker_results', durable=True)


def callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    data = json.loads(body)

    try:
        task = data['task']
        logger.info('Performing {}...'.format(task))

        if task == 'text_normalize':
            output_name = text.normalize(work_dir, data['input'])
        elif task == 'ffmpeg':
            output_name = audio.ffmpeg(work_dir, data['input'])
        elif task == 'forcealign':
            output_name = speech.forcealign(work_dir, data['audio'], data['transcript'])
        elif task == 'segmentalign':
            output_name = speech.segmentalign(work_dir, data['audio'], data['transcript'])
        elif task == 'recognize':
            output_name = speech.recognize(work_dir, data['input'])
        # elif task == 'emupackage':
        #     output_name = package(work_dir, data['project'], db)
        else:
            raise RuntimeError('unknown task: ' + task)

        result = {'id': data['id'], 'output': output_name}

        channel.basic_publish(exchange='', routing_key='worker_results', body=json.dumps(result))

    except RuntimeError as e:
        logger.exception('Worker error')

        result = {'id': data['id'], 'error': str(e)}
        channel.basic_publish(exchange='', routing_key='worker_results', body=json.dumps(result))


def run():
    logger.info('Worker queue waiting...')

    channel.basic_consume(callback, queue='workers')
    try:
        channel.start_consuming()
    except:
        logger.exception('Channel error')
