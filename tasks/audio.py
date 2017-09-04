import os
from subprocess import call, STDOUT
from tempfile import mkstemp


def ffmpeg(dir, file):
    fd, tmp = mkstemp(dir=dir, suffix='.wav')
    os.close(fd)

    cmd = ['ffmpeg', '-y', '-i', os.path.join(dir, file), '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16k', tmp]
    try:
        with open(tmp + '_ffmpeg.log', 'w') as f:
            call(cmd, stdout=f, stderr=STDOUT)
    except:
        raise RuntimeError('error in call cmd -- check ' + tmp + '_ffmpeg.log')

    if os.path.exists(tmp):
        return os.path.basename(tmp)
    else:
        raise RuntimeError('error in ffmpeg (no output file) -- check ' + tmp + '_ffmpeg.log')
