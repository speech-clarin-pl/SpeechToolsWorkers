import logging
from pathlib import Path

logger = logging.getLogger('worker')

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

work_dir = Path('/work')

# TODO set this somhow?
transcribe_word_url = 'http://mowa.clarin-pl.eu/tools/phonetize/word/'
