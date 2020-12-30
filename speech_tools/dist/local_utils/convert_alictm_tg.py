#!/usr/bin/env python
import argparse
import re
from pathlib import Path

from textgrid import TextGrid, IntervalTier

besi = re.compile(r'^.*_[BESI]$')


def convert_ctm_to_textgrid(ctm, textgrid):
    words = []
    phonemes = []
    with open(ctm, encoding='utf-8') as f:
        for l in f:
            tok = l.strip().split()
            text = tok[4]
            beg = float(tok[2])
            dur = float(tok[3])
            if tok[0][0] == '@':
                if besi.match(text):
                    text = text[:-2]
                phonemes.append((text, beg, dur))
            else:
                words.append((text, beg, dur))
    tw = IntervalTier(name='words')
    tp = IntervalTier(name='phonemes')
    for seg in words:
        try:
            tw.add(round(seg[1], 2), round(seg[1] + seg[2], 2), seg[0])
        except ValueError:
            print("Error in word seg: " + seg[0])
    for seg in phonemes:
        try:
            tp.add(round(seg[1], 2), round(seg[1] + seg[2], 2), seg[0])
        except ValueError:
            print("Error in phoneme seg: " + seg[0])
    tg = TextGrid()
    tg.append(tw)
    tg.append(tp)
    tg.write(textgrid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts CTM with word and phoneme level alignment to TextGrid')
    parser.add_argument('ctm', help='Alignment CTM file(s)', type=Path)
    parser.add_argument('tg', help='TextGrid', type=Path)

    args = parser.parse_args()

    convert_ctm_to_textgrid(args.ctm, args.tg)
