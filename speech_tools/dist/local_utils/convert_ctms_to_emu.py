#!/usr/bin/env python
import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

besi = re.compile(r'^.*_[BESI]$')


def load_ctm(ctm: Path, has_phonemes: bool = False):
    ret = []
    ret2 = []
    with open(str(ctm)) as f:
        for l in f:
            tok = l.strip().split()
            text = tok[4]
            beg = float(tok[2])
            dur = float(tok[3])
            if has_phonemes and tok[0][0] == '@':
                if besi.match(text):
                    text = text[:-2]
                ret2.append((text, beg, dur))
            else:
                ret.append((text, beg, dur))
    if has_phonemes:
        return ret, ret2
    else:
        return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('wav', type=Path)
    parser.add_argument('name', type=str)
    parser.add_argument('vad_ctm', type=Path)
    parser.add_argument('dia_ctm', type=Path)
    parser.add_argument('ali_ctm', type=Path)
    parser.add_argument('out_json', type=Path)
    parser.add_argument('--samplerate', '-fs', type=float, default=16000.0)

    args = parser.parse_args()

    id = 0
    sr = args.samplerate

    ret = OrderedDict()
    levels = []

    ret['sampleRate'] = args.samplerate
    ret['annotates'] = args.wav.name
    ret['name'] = args.name
    ret['levels'] = levels
    ret['links'] = []

    segs = []
    for seg in load_ctm(args.vad_ctm):
        segs.append({'id': id, 'sampleStart': seg[1] * sr, 'sampleDur': seg[2] * sr,
                     'labels': [{'name': 'VAD', 'value': seg[0]}]})
        id += 1
    levels.append({'name': 'VAD', 'type': 'SEGMENT', 'items': segs})

    segs = []
    for seg in load_ctm(args.dia_ctm):
        segs.append({'id': id, 'sampleStart': seg[1] * sr, 'sampleDur': seg[2] * sr,
                     'labels': [{'name': 'Speaker', 'value': seg[0]}]})
        id += 1
    levels.append({'name': 'Speaker', 'type': 'SEGMENT', 'items': segs})

    words, phs = load_ctm(args.ali_ctm, has_phonemes=True)

    segs = []
    for seg in words:
        segs.append({'id': id, 'sampleStart': seg[1] * sr, 'sampleDur': seg[2] * sr,
                     'labels': [{'name': 'Word', 'value': seg[0]}]})
        id += 1
    levels.append({'name': 'Word', 'type': 'SEGMENT', 'items': segs})

    segs = []
    for seg in phs:
        segs.append({'id': id, 'sampleStart': seg[1] * sr, 'sampleDur': seg[2] * sr,
                     'labels': [{'name': 'Phoneme', 'value': seg[0]}]})
        id += 1
    levels.append({'name': 'Phoneme', 'type': 'SEGMENT', 'items': segs})

    with open(args.out_json, 'w') as f:
        json.dump(ret, f, indent=4)
