import ffmpeg
import normalization
import speech

workers = {'ffmpeg': ffmpeg.run, 'normalization': normalization.run, 'speech': speech.run}