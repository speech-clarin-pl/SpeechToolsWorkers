from pathlib import Path
from subprocess import STDOUT, run
from tempfile import NamedTemporaryFile

from worker.config import logger


def ffmpeg(dir: Path, file: str) -> str:
    with NamedTemporaryFile(dir=dir, suffix='.wav') as f:
        tmp = Path(f.name)

    cmd = ['ffmpeg', '-y', '-i', dir / file, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16k', str(tmp)]
    logger.info(u'Running {}'.format(' '.join(cmd)))
    try:
        with open(str(tmp) + '_ffmpeg.log', 'w') as f:
            run(cmd, stdout=f, stderr=STDOUT, check=True)
    except:
        raise RuntimeError('error in call cmd -- check ' + str(tmp) + '_ffmpeg.log')

    if tmp.exists():
        return tmp
    else:
        raise RuntimeError('error in ffmpeg (no output file) -- check ' + str(tmp) + '_ffmpeg.log')
