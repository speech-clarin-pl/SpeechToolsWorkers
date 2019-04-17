import re
from collections import OrderedDict

from worker.tasks.emu import ID

EPSILON = 5e-3


class Segment:
    def __init__(self, line=''):

        if len(line) == 0:
            self.id = ID.next()
            self.file = ''
            self.channel = ''
            self.start = 0
            self.dur = 0
            self.end = 0
            self.text = ''
            return

        tok = re.split('\\s+', line)

        if len(tok) < 5:
            raise RuntimeError(f'Expected line to have at least 5 tokens (found {len(tok)})')

        self.id = ID.next()
        self.file = tok[0]
        self.channel = tok[1]
        self.start = float(tok[2])
        self.dur = float(tok[3])
        self.end = self.start + self.dur
        self.text = tok[4]

    def wraps(self, other):
        return other.start - self.start > -EPSILON and other.end - self.end < EPSILON


class CTM:
    def __init__(self, name):
        self.name = name
        self.segments = []
        self.besi = re.compile('^.*_[BESI]$')

    def get_annotation(self, name, labelname, samplerate=16000, get_segments=True, rmbesi=False):

        level = OrderedDict()

        level['name'] = name
        if get_segments:
            level['type'] = 'SEGMENT'
        else:
            level['type'] = 'ITEM'

        items = []
        level['items'] = items

        for seg in self.segments:
            item = OrderedDict()
            items.append(item)

            item['id'] = seg.id

            if get_segments:
                item['sampleStart'] = int(samplerate * seg.start)
                item['sampleDur'] = int(samplerate * seg.dur)

            labels = []
            item['labels'] = labels

            label = OrderedDict()
            labels.append(label)

            label['name'] = labelname
            if rmbesi:
                text = seg.text
                if self.besi.match(text):
                    text = text[:-2]
                label['value'] = text
            else:
                label['value'] = seg.text

        return level

    def get_links(self, other_ctm):

        links = []

        for seg in self.segments:
            for other_seg in other_ctm.segments:
                if seg.file == other_seg.file and seg.wraps(other_seg):
                    link = OrderedDict()
                    links.append(link)
                    link['fromID'] = seg.id
                    link['toID'] = other_seg.id

        return links

    def get_utt_file(self):
        ctm = CTM(self.name)
        min = max = 0

        for seg in self.segments:
            if min > seg.start:
                min = seg.start
            if max < seg.end:
                max = seg.end

        seg = Segment()

        seg.start = min
        seg.end = max
        seg.dur = max - min
        seg.text = self.name

        seg.file = self.name
        seg.channel = self.segments[0].channel

        ctm.segments.append(seg)
        return ctm


def load_ctm(file, name):
    words = CTM(name)
    phonemes = CTM(name)
    with open(file) as f:
        for num, line in enumerate(f):
            try:
                seg = Segment(line.strip())
            except Exception as err:
                raise RuntimeError(err, f'Error in {file}:{num} >{line.strip()}<')
            if line[0] == '@':
                phonemes.segments.append(seg)
            else:
                words.segments.append(seg)

    words.segments = sorted(words.segments, key=lambda seg: seg.start)
    phonemes.segments = sorted(phonemes.segments, key=lambda seg: seg.start)
    return words, phonemes
