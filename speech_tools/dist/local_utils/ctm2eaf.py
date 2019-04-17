import argparse
from pathlib import Path

from pympi.Elan import Eaf, to_eaf


def read_ctm(ctm_path, seg2tier, eaf):
    ret = {}
    with open(ctm_path) as f:
        for l in f:
            tok = l.strip().split()
            id = tok[0]
            utt_id = id.split('_')[-1]
            tier = seg2tier[utt_id]
            start = float(tok[2])
            len = float(tok[3])
            text = tok[4]

            e_utt = eaf.tiers[tier][0][utt_id]
            e_start = eaf.timeslots[e_utt[0]]

            if tier not in ret:
                ret[tier] = []
            ret[tier].append((e_start + int(start * 1000), e_start + int((start + len) * 1000), text))

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('words_ctm', type=Path)
    parser.add_argument('seg2tier', type=Path)
    parser.add_argument('eaf_in', type=Path)
    parser.add_argument('eaf_out', type=Path)
    parser.add_argument('--phones-ctm', default=None, type=Path)

    args = parser.parse_args()

    words_ctm_path = args.words_ctm
    seg2tier_path = args.seg2tier
    eaf_in_path = args.eaf_in
    eaf_out_path = args.eaf_out

    eaf = Eaf(str(eaf_in_path))

    seg2tier = {}
    with open(seg2tier_path) as f:
        for l in f:
            tok = l.strip().split()
            seg2tier[tok[0]] = tok[1]

    tiers = read_ctm(words_ctm_path, seg2tier, eaf)

    for tier in tiers.keys():
        part = eaf.tiers[tier][2]['PARTICIPANT']
        t = eaf.add_tier('{}_words'.format(tier), parent='tier', part=part, ann='Clarin-PL-service')

    for tier, segs in tiers.items():
        for seg in segs:
            eaf.add_annotation('{}_words'.format(tier), seg[0], seg[1], seg[2])

    if args.phones_ctm:
        phones_ctm_path = args.phones_ctm
        tiers = read_ctm(phones_ctm_path, seg2tier, eaf)

        for tier in tiers.keys():
            part = eaf.tiers[tier][2]['PARTICIPANT']
            t = eaf.add_tier('{}_phones'.format(tier), parent='tier', part=part, ann='Clarin-PL-service')

        for tier, segs in tiers.items():
            for seg in segs:
                eaf.add_annotation('{}_phones'.format(tier), seg[0], seg[1], seg[2])

    to_eaf(str(eaf_out_path), eaf)
