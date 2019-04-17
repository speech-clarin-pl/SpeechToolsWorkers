import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from worker.config import logger

pat = re.compile(r'[^\w\s]', flags=re.U)
num = re.compile(r'[0-9]', flags=re.U)
ws = re.compile(r'\s+', flags=re.U)


def normalize(dir: Path, file: str):
    with NamedTemporaryFile(dir=dir, suffix='.wav') as f:
        output = Path(f.name)
    outputname = output.name
    logger.info(f'Normalizing text file {file} -> {outputname}')
    with open(str(dir / file)) as fin:
        with open(output, 'w') as fout:
            for line in fin:
                line = line.lower()
                line = pat.sub(' ', line)
                line = num.sub(' ', line)
                line = ws.sub(' ', line)
                fout.write(line)
    return output
