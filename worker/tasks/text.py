import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict

from worker.config import logger, work_dir

pat = re.compile(r'[^\w\s]', flags=re.U)
num = re.compile(r'[0-9]', flags=re.U)
ws = re.compile(r'\s+', flags=re.U)


def normalize(task: Dict[str, any]) -> Path:
    file = work_dir / task['input']
    with NamedTemporaryFile(dir=work_dir, suffix='.txt', delete=False) as fout:
        output = Path(fout.name)
        logger.info(f'Normalizing text file {file} -> {fout.name}')
        with open(str(work_dir / file)) as fin:
            for line in fin:
                line = line.lower()
                line = pat.sub(' ', line)
                line = num.sub(' ', line)
                line = ws.sub(' ', line)
                fout.write(line)
    return output.relative_to(work_dir)
