import codecs
import json
from collections import OrderedDict

from worker.tasks.emu import ID
from worker.tasks.emu.CTM import load_ctm


def save_annot(ctm_file, annot_file, name, samplerate=16000.0):
    ID.reset()

    words_file, phonemes_file = load_ctm(ctm_file, name)
    utterance = words_file.get_utt_file()

    annot = OrderedDict()

    annot['name'] = name
    annot['annotates'] = name + '.wav'
    annot['sampleRate'] = samplerate

    levels = []
    annot['levels'] = levels

    levels.append(utterance.get_annotation('Utterance', 'Utterance', get_segments=False))

    levels.append(words_file.get_annotation('Word', 'Word', samplerate))

    # syllables = Syllables(words_file, phonemes_file)
    # levels.append(syllables.getWordAnnotation('Syllable', 'Syllable', 'Stress'))
    # levels.append(syllables.getPhonemeAnnotation('Phonetic Syllable', 'Syllable', 'Stress'))

    levels.append(phonemes_file.get_annotation('Phoneme', 'Phoneme', samplerate, rmbesi=True))

    uttlinks = utterance.get_links(words_file)
    wordlinks = words_file.get_links(phonemes_file)
    # syllinks = syllables.getLinks()

    annot['links'] = uttlinks + wordlinks

    with codecs.open(annot_file, mode='w', encoding='utf-8') as f:
        json.dump(annot, f, indent=4)
