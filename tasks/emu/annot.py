import codecs
import json
from collections import OrderedDict

from tasks.emu import ID
from tasks.emu.CTM import load_ctm


def save_annot(ctm_file, annot_file, name, samplerate=16000.0):
    ID.reset()

    words_file, phonemes_file = load_ctm(ctm_file, name)
    utterance = words_file.getUttFile()

    annot = OrderedDict()

    annot['name'] = name
    annot['annotates'] = name + '.wav'
    annot['sampleRate'] = samplerate

    levels = []
    annot['levels'] = levels

    levels.append(utterance.getAnnotation('Utterance', 'Utterance', get_segments=False))

    levels.append(words_file.getAnnotation('Word', 'Word', samplerate))

    # syllables = Syllables(words_file, phonemes_file)
    # levels.append(syllables.getWordAnnotation('Syllable', 'Syllable', 'Stress'))
    # levels.append(syllables.getPhonemeAnnotation('Phonetic Syllable', 'Syllable', 'Stress'))

    levels.append(phonemes_file.getAnnotation('Phoneme', 'Phoneme', samplerate, rmbesi=True))

    uttlinks = utterance.getLinks(words_file)
    wordlinks = words_file.getLinks(phonemes_file)
    # syllinks = syllables.getLinks()

    annot['links'] = uttlinks + wordlinks

    with codecs.open(annot_file, mode='w', encoding='utf-8') as f:
        json.dump(annot, f, indent=4)
