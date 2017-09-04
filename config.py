import logging

import pika
from pymongo import MongoClient

logger = logging.getLogger('worker')
db = MongoClient()
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
