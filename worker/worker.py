from time import sleep

from bson import ObjectId
from pymongo import ASCENDING

from worker.config import logger, db_host, max_task_history, ave_task_size
from worker.tasks import tasks_map


def run():
    while True:
        from pymongo import MongoClient

        db = MongoClient(host=db_host)
        # if 'tasks' not in db.workers.list_collection_names():
        #     db.workers.create_collection('tasks', capped=True, max=max_task_history,
        #                                  size=max_task_history * ave_task_size)

        logger.info('Worker queue waiting...')

        while True:

            sleep(1)

            task_data = db.workers.tasks.find_one_and_update(filter={'$and': [{'in_progress': False}, {'done': False}]},
                                                            update={'$set': {'in_progress': True}},
                                                            sort=[('time', ASCENDING)])

            if not task_data:
                continue

            task_type = task_data['task']
            logger.info(f'Performing {task_type}...')

            set = {'done': True, 'in_progress': False}
            if task_type in tasks_map:
                run = tasks_map[task_type]
                try:
                    result = run(task_data)
                    set['result'] = str(result)
                except RuntimeError as e:
                    set['error'] = str(e)
            else:
                logger.error(f'Unknown task: {task_type}')
                set['error'] = f'Unknown task: {task_type}'

            db.workers.tasks.update_one({'_id': ObjectId(task_data['_id'])}, {'$set': set})
