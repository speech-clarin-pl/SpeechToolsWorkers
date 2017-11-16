import os
from subprocess import Popen, STDOUT
from tempfile import mkdtemp

from config import logger


def align(tool_dir, wav_file, txt_file, output):
    cmd = ['bash', u'./speech_tools/{}/run.sh'.format(tool_dir), wav_file, txt_file, output]
    with open(os.path.join(output, 'log.txt'), 'w') as log:
        logger.info(u'Running {}'.format(' '.join(cmd)))
        proc = Popen(cmd, stdout=log, stderr=STDOUT)
        ret = proc.wait()
    if ret != 0:
        raise RuntimeError('error running script in {}'.format(output))
    if not os.path.exists(os.path.join(output, 'output.ctm')):
        raise RuntimeError('output.ctm missing')


def reco(wav_file, output):
    cmd = ['bash', './speech_tools/Recognize/run.sh', wav_file, output]
    with open(os.path.join(output, 'log.txt'), 'w') as log:
        logger.info(u'Running {}'.format(' '.join(cmd)))
        proc = Popen(cmd, stdout=log, stderr=STDOUT)
        ret = proc.wait()
    if ret != 0:
        raise RuntimeError('error running script in {}'.format(output))
    if not os.path.exists(os.path.join(output, 'output.txt')):
        raise RuntimeError('output.txt missing')


def forcealign(work_dir, audio, txt):
    dir = mkdtemp(dir=work_dir)
    try:
        align('ForcedAlign', os.path.join(work_dir, audio), os.path.join(work_dir, txt), dir)
    except RuntimeError:
        logger.warn('Forced align failed! Retrying with Segment...')
        return segmentalign(work_dir, audio, txt)
    return os.path.join(dir, 'output.ctm')


def segmentalign(work_dir, audio, txt):
    dir = mkdtemp(dir=work_dir)
    align('SegmentAlign', os.path.join(work_dir, audio), os.path.join(work_dir, txt), dir)
    return os.path.join(dir, 'output.ctm')


def recognize(work_dir, audio):
    dir = mkdtemp(dir=work_dir)
    reco(os.path.join(work_dir, audio), dir)
    return os.path.join(dir, 'output.txt')
