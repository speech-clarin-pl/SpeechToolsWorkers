# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
from collections import OrderedDict

from pyphen import Pyphen

import ID
#
# sylaby akcentowane
#
# Akcent wyrazowy jest w zasadzie stały i pada na przedostatnią sylabę.
#
# Od reguły tej są wyjątki. Zgodnie z normą wzorcową akcent pada:
#
#     na trzecią sylabę od końca w formach 1. i 2. os. lm. czasu przeszłego (czytaliśmy, pisaliście),
#           w lp. i 3. os. lm. trybu przypuszczającego (zrobiłbym, narysowaliby) oraz w wyrazach zapożyczonych
#           zakończonych na -ika, -yka, (gramatyka, mechanika, metryka, metafizyka, lektyka, leksyka, matematyka,
#           semantyka itd.), a także w liczebnikach z cząstkami: -kroć, -sta, -set (siedemset, czterysta, osiemset)
#           i spójnikach połączonych z końcówkami osobowymi czasownika (abyśmy, żebyście);
#     na czwartą sylabę od końca form 1. i 2. os. lm. trybu przypuszczającego (obejrzelibyśmy, po zna li by śmy);
#     na piątą sylabę od końca w formach 1. i 2. os. lm. trybu przypuszczającego czasowników połączonych z się
#          (dowiedzielibyście się, oburzylibyśmy się);
#     na ostatnią sylabę w rzeczownikach jednosylabowych z cząstkami: arcy-, wice-, eks- (arcymistrz, eksmąż, wicekról);
#     w niektórych wyrazach dopuszczalne jest akcentowanie zmienne: analiza lub analiza, epoka lub epoka,
#           festiwal lub festiwal, reguła lub reguła, w ogóle albo w ogóle (nie: wogle);
#     zwyczajowo niektóre wyrazy akcentuje się na trzeciej sylabie od końca: maksimum, minimum, prezydent,
#           Rzeczpospolita, uniwersytet;
#     przejęte z łaciny wyrazy w innych przypadkach niż mianownik akcentuje się na trzeciej sylabie od końca wtedy,
#           kiedy mają tyle samo sylab, co mianownik, np. polemika, polemiki, ale: polemikami; lektyka, lektyce, ale: lektykami.
#
# I jeszcze przypomnienie:
# Wyrazy obce, które są w językach pochodzenia akcentowane na drugiej sylabie od końca albo niepochodzące z łaciny klasycznej, akcentujemy na tej sylabie: biblioteka, episkopat, kapitan, liceum, muzeum, panaceum, oficer, wizyta, atmosfera.
#
from config import transcribe_word_url


class Syllable:
    def __init__(self, syl):
        self.id = ID.next()
        self.text = syl
        self.phonemes = []
        self.stressed = False

    def __str__(self):
        arr = []
        for ph in self.phonemes:
            arr.append(unicode(ph.text))
        return u'{} ({})'.format(self.text, arr)


hyp = Pyphen(lang='pl_PL')

ph_map = {'I': 'y', 'en': u'ę', 'on': u'ą', 'v': 'w', 'S': 'sz', 'Z': u'ż', 'si': u'ś', 'zi': u'ź', 'x': 'h', 'ts': 'c',
          'tS': 'cz', 'dZ': u'dż', 'ni': u'ń', 'tsi': u'ć', 'dzi': u'dź', 'N': 'n', 'w': u'ł'}


def transcribe(word):
    ret = []
    if not word:
        return ret
    url = transcribe_word_url + urllib.quote_plus(word.encode('utf-8'))
    trans = json.loads(urllib2.urlopen(url).read())
    for t in trans:
        ret.append(t.split(' '))
    return ret


def phonemes_to_word(phonemes):
    phonemes = list(phonemes)
    for i, ph in enumerate(phonemes):
        if ph in ph_map:
            phonemes[i] = ph_map[ph]
    return ''.join(phonemes)


stress_exceptions = set(['maksimum', 'minimum', 'rzeczpospolita', 'uniwersytet', 'mianownik', 'polemika'])


class Word:
    def __init__(self, word, phonemes):
        self.word = word
        self.word_syllables = []
        for syl in hyp.inserted(word.text).split('-'):
            self.word_syllables.append(Syllable(syl))
        self.phonemes = phonemes_to_word(phonemes)
        self.ph_syllables = []
        for syl in hyp.inserted(self.phonemes).split('-'):
            self.ph_syllables.append(Syllable(syl))

    def apply_stress(self):
        s_pos = - 2
        word = self.word.text

        if word.endswith(u'iśmy') or word.endswith(u'iście'):
            s_pos = - 3

        if word.endswith(u'ibyśmy') or word.endswith(u'ibyście'):
            s_pos = - 4

        if word.startswith(u'arcy') or word.startswith(u'wice') or word.startswith(u'eks') or word.startswith(u'super'):
            if len(self.word_syllables) == 2:
                s_pos = -1

        if word in stress_exceptions:
            s_pos = - 3

        if len(self.word_syllables) + s_pos < 0:
            s_pos += 1

        self.word_syllables[s_pos].stressed = True

        if len(self.ph_syllables) + s_pos < 0:
            s_pos += 1

        self.ph_syllables[s_pos].stressed = True

    def __str__(self):
        arr = []
        for syl in self.word_syllables:
            arr.append(unicode(syl))
        arr_ph = []
        for syl in self.ph_syllables:
            arr_ph.append(unicode(syl))

        return u'{}\n{}\n>>{}\n>>{}'.format(self.word.text, arr, self.phonemes, arr_ph)


class Syllables:
    def __init__(self, word_file, phoneme_file, rm_besi=True):
        self.words = []
        self.rm_besi = rm_besi

        for seg in word_file.segments:

            phonemes = []
            phoneme_tr = []
            for ph in phoneme_file.segments:
                if seg.file == ph.file and seg.wraps(ph):
                    phonemes.append(ph)
                    pht = ph.text
                    if rm_besi:
                        pht = pht[:-2]
                    phoneme_tr.append(pht)

            word = Word(seg, phoneme_tr)
            self.words.append(word)

            word_output = self.match_syllables(word.word_syllables, phonemes, phoneme_tr)
            if word_output:
                assert len(word_output) == len(word.word_syllables)
                for i in range(len(word.word_syllables)):
                    word.word_syllables[i].phonemes = word_output[i]

            ph_output = self.match_syllables(word.ph_syllables, phonemes, phoneme_tr)
            if ph_output:
                assert len(ph_output) == len(word.ph_syllables)
                for i in range(len(word.ph_syllables)):
                    word.ph_syllables[i].phonemes = ph_output[i]

            word.apply_stress()

            if len(word.word_syllables[0].phonemes) == 0:
                if len(word.word_syllables) != len(word.ph_syllables):
                    # print 'WARNING: word and phoneme syllables count mismatch: ' + unicode(word)
                    pass
                else:
                    for i, syl in enumerate(word.ph_syllables):
                        word.word_syllables[i].phonemes = syl.phonemes

                        # print u'Added: ' + unicode(word)

    def match_syllables(self, syllables, phonemes, phoneme_tr):
        stack = [(phonemes, phoneme_tr, 0, [])]
        # stack >> phoneme list, phoneme transcription, syllable index, output
        while len(stack) > 0:
            ph, ph_tr, syl_idx, out = stack.pop()

            if syl_idx >= len(syllables):
                if len(ph) == 0:
                    return out
                else:
                    continue

            syl = syllables[syl_idx]
            for trans in transcribe(syl.text):
                tr_num = len(trans)
                if tr_num <= len(ph_tr) and trans == ph_tr[:tr_num]:
                    out_list = list(out)
                    out_list.append(ph[:tr_num])
                    stack.append((ph[tr_num:], ph_tr[tr_num:], syl_idx + 1, out_list))

        return None

    def getWordAnnotation(self, name, labelname, stresslabel):
        level = OrderedDict()

        level['name'] = name
        level['type'] = 'ITEM'

        items = []
        level['items'] = items

        for word in self.words:
            for syl in word.word_syllables:
                item = OrderedDict()
                items.append(item)

                item['id'] = syl.id

                labels = []
                item['labels'] = labels

                label = OrderedDict()
                labels.append(label)

                label['name'] = labelname
                label['value'] = syl.text

                label = OrderedDict()
                labels.append(label)

                label['name'] = stresslabel
                if syl.stressed:
                    label['value'] = 'yes'
                else:
                    label['value'] = 'no'

        return level

    def getPhonemeAnnotation(self, name, labelname, stresslabel):
        level = OrderedDict()

        level['name'] = name
        level['type'] = 'ITEM'

        items = []
        level['items'] = items

        for word in self.words:
            for syl in word.ph_syllables:
                item = OrderedDict()
                items.append(item)

                item['id'] = syl.id

                labels = []
                item['labels'] = labels

                label = OrderedDict()
                labels.append(label)

                label['name'] = labelname
                label['value'] = syl.text

                label = OrderedDict()
                labels.append(label)

                label['name'] = stresslabel
                if syl.stressed:
                    label['value'] = 'yes'
                else:
                    label['value'] = 'no'

        return level

    def getLinks(self):
        links = []

        for word in self.words:
            for syl in word.word_syllables:
                link = OrderedDict()
                links.append(link)
                link['fromID'] = word.word.id
                link['toID'] = syl.id

                for ph in syl.phonemes:
                    link = OrderedDict()
                    links.append(link)
                    link['fromID'] = syl.id
                    link['toID'] = ph.id

        for word in self.words:
            for syl in word.ph_syllables:
                link = OrderedDict()
                links.append(link)
                link['fromID'] = word.word.id
                link['toID'] = syl.id

                for ph in syl.phonemes:
                    link = OrderedDict()
                    links.append(link)
                    link['fromID'] = syl.id
                    link['toID'] = ph.id

        return links
