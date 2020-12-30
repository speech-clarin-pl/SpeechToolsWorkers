import logging
import os
from pathlib import Path

logger = logging.getLogger('worker')

work_dir = Path('/work')
tmp_dir = Path('/tmp')
db_host = 'localhost'
db_name = 'workers'
max_task_history = 1000
ave_task_size = 100

# TODO set this somhow?
transcribe_word_url = 'http://mowa.clarin-pl.eu/tools/phonetize/word/'

speech_tools_path = (Path(__file__).parent.parent / 'speech_tools').absolute()

if 'DB_HOST' in os.environ:
    db_host = os.environ['DB_HOST']

if 'DB_NAME' in os.environ:
    db_name = os.environ['DB_NAME']

if 'TOOLS' in os.environ:
    speech_tools_path = (Path(os.environ['TOOLS'])).absolute()

assert speech_tools_path.exists(), f'Missing path {speech_tools_path}'
