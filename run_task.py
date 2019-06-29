import argparse
from datetime import datetime
from time import sleep

from bson import ObjectId
from pymongo import MongoClient

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-host', default='localhost')
    parser.add_argument('task')
    parser.add_argument('input', nargs='+')

    args = parser.parse_args()

    task_type = args.task
    task_inputs = args.input

    task = {'task': task_type, 'in_progress': False, 'done': False, 'time': datetime.utcnow()}

    if task_type == 'text_normalize' or task_type == 'ffmpeg' or task_type == 'recognize' or task_type == 'diarize' or task_type == 'vad':
        task['input'] = task_inputs[0]
    elif task_type == 'forcealign' or task_type == 'segmentalign':
        task['input']={}
        task['input']['audio'] = task_inputs[0]
        task['input']['text'] = task_inputs[1]
    elif task_type == 'kws':
        task['input'] = {}
        task['input']['audio'] = task_inputs[0]
        task['input']['keywords'] = task_inputs[0]
    else:
        raise RuntimeError(f'Unknown task {task_type}!')

    db = MongoClient(host=args.db_host)

    ret = db.workers.tasks.insert_one(task)

    id = ret.inserted_id

    print(f'Created task {id}!')

    print('Waiting for completion...')

    while True:
        sleep(1)
        t = db.workers.tasks.find_one({'_id': ObjectId(id)})
        if (t['done']):
            break

    print('Task done!')

    if 'result' in t:
        print(f'Result: {t["result"]}')
    else:
        print(f'Result: {t["error"]}')
