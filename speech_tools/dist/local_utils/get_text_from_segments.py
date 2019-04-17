import argparse


class Segment:
    def __init__(self, time_line):
        tok = time_line.split(' ')
        assert len(tok) == 4, f'segments file line has to have 4 tokens: {time_line}'

        self.file = tok[1]
        self.segment = tok[0]
        self.start = float(tok[2])
        self.end = float(tok[3])
        self.text = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('seg_text')
    parser.add_argument('seg_times')
    parser.add_argument('text')

    args = parser.parse_args()

    segments = {}
    with open(args.seg_times) as f:
        for line in f:
            seg = Segment(line)
            segments[seg.segment] = seg

    with open(args.seg_text) as f:
        for line in f:
            pos = line.find(' ')
            assert pos > 0, f'cannot parse text line: {line}'
            seg_id = line[:pos]
            seg = segments[seg_id]
            seg.text = line[pos + 1:].strip()

    files = {}
    for seg in segments.values():
        if not seg.file in files:
            files[seg.file] = []
        files[seg.file].append(seg)

    with open(args.text, 'w') as f:
        for segments in files.values():
            segments = sorted(segments, key=lambda seg: seg.start)
            text = segments[0].text
            for seg in segments[1:]:
                text += ' ' + seg.text
            f.write(f'{segments[0].file} {text}\n')
