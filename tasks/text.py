import codecs
import os
import re
from tempfile import mkstemp

from config import logger

pat = re.compile('[^\w\s]', flags=re.U)
num = re.compile('[0-9]', flags=re.U)
ws = re.compile('\s+', flags=re.U)


def normalize(dir, file):
    fd, output = mkstemp(dir=dir)
    os.close(fd)
    outputname = os.path.basename(output)
    logger.info(u'Normalizing text file {} -> {}'.format(file, outputname))
    with codecs.open(os.path.join(dir, file), encoding='utf8') as fin:
        with codecs.open(output, 'w', encoding='utf8') as fout:
            for line in fin:
                line = line.lower()
                line = pat.sub(' ', line)
                line = num.sub(' ', line)
                line = ws.sub(' ', line)
                fout.write(line)
    return outputname
