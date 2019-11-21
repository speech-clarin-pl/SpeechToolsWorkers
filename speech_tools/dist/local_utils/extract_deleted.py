import argparse


class Segment:
    def __init__(self, line):
        tok = line.strip().split(' ')
        assert len(tok) == 8, 'Line should have exactly 8 tokens in CTMali file:\n|{}|'.format(line.strip())
        self.file = tok[0]
        self.channel = tok[1]
        self.start = float(tok[2])
        self.dur = float(tok[3])
        self.hyp = tok[4]
        self.conf = tok[5]
        self.ref = tok[6]
        self.op = tok[7]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ctm')
    parser.add_argument('text')
    parser.add_argument('segments')

    args = parser.parse_args()

    segments = []

    with open(args.ctm,encoding='utf-8') as f:
        for line in f:
            segments.append(Segment(line))

    segments = sorted(segments, key=lambda segment: segment.start)

    seg_text = ''
    seg_start = 0
    seg_id = 1
    file_id = ''

    with open(args.text, mode='w', encoding='utf-8') as tf, open(args.segments, 'w') as sf:
        for seg in segments:
            if seg.op == 'del' or seg.op == 'sub':
                seg_text = seg_text + ' ' + seg.ref
                file_id = seg.file
                if seg_start == 0:
                    seg_start = seg.start
            else:
                if seg.start == seg_start:
                    continue
                if len(seg_text) > 0:
                    tf.write('{}-{}{}\n'.format(file_id,seg_id,seg_text))
                    seg_text = ''
                    sf.write('{}-{} {} {} {}\n'.format(file_id,seg_id,file_id,seg_start,seg.start))
                    seg_start = 0
                    seg_id += 1
