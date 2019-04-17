import argparse
import re
from pathlib import Path

from pympi.Elan import Eaf

re_pat = re.compile('[^\w\s]', flags=re.U)
re_num = re.compile('[0-9]', flags=re.U)


def normalize(text):
    text = text.lower()
    text = re_pat.sub(' ', text)
    text = re_num.sub(' ', text)
    return ' '.join(text.split())


class Segment:
    def __init__(self, id, start, end, text, spk, tier):
        self.id = id
        self.start = start / 1000.0
        self.end = end / 1000.0
        self.text = normalize(text)
        self.spk = spk
        self.tier = tier


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts an EAF file into a Kaldi data dir')
    parser.add_argument('eaf', help='Input EAF file')
    parser.add_argument('data', help='Output data directory')
    parser.add_argument('--skip-tiers', help='Comma-separated list of tiers to skip.')
    parser.add_argument('--spk-tier', action='store_true',
                        help='Each tier is one speaker, otherwise each segment is new speaker.')

    args = parser.parse_args()

    eaf_path = Path(args.eaf)
    data_path = Path(args.data)
    spk_tier = args.spk_tier

    data_path.mkdir(exist_ok=True)

    eaf = Eaf(str(eaf_path))

    segments = []
    tier_names = list(eaf.tiers.keys())
    if args.skip_tiers:
        for t in args.skip_tiers.split(','):
            tier_names.remove(t)

    num = 1
    for t in tier_names:
        for id, s in eaf.tiers[t][0].items():
            start = eaf.timeslots[s[0]]
            end = eaf.timeslots[s[1]]
            text = s[2].strip()
            if spk_tier:
                spk = t + '_'
            else:
                spk = f'spk{num:02d}'
                num += 1
            segments.append(Segment(id, start, end, text, spk, t))

    with open(str(data_path / 'text'), mode='w') as f:
        for seg in segments:
            f.write(f'{seg.spk}_{seg.id} {seg.text}\n')

    with open(str(data_path / 'segments'), mode='w') as f:
        for seg in segments:
            f.write(f'{seg.spk}_{seg.id} input {seg.start} {seg.end}\n')

    with open(str(data_path / 'utt2spk'), mode='w') as f:
        for seg in segments:
            f.write(f'{seg.spk}_{seg.id} {seg.spk}\n')

    with open(str(data_path / 'seg2tier'), mode='w') as f:
        for seg in segments:
            f.write(f'{seg.id} {seg.tier}\n')
