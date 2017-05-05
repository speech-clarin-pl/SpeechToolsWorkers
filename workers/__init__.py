import logging

logger = logging.getLogger('worker')


def ffmpeg():
    import ffmpeg
    ffmpeg.run()


def normalization():
    import normalization
    normalization.run()


def speech():
    import speech
    speech.run()


workers = {'ffmpeg': ffmpeg, 'normalization': normalization, 'speech': speech}
