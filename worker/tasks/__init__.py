from worker.tasks import text, audio, speech, emu

tasks_map = {'text_normalize': text.normalize,
             'ffmpeg': audio.ffmpeg,
             'forcealign': speech.forcealign,
             'segmentalign': speech.segmentalign,
             'recognize': speech.recognize,
             'diarize': speech.diarize,
             'vad': speech.vad,
             'kws': speech.kws}

# 'emupackage': emu.task.package -- cannot be done in this version
