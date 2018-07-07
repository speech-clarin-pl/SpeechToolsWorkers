import argparse

parser = argparse.ArgumentParser(description='Fixes CTM file to sort and remove overlaping segments.')

parser.add_argument('input_ctm')
parser.add_argument('output_ctm')

args = parser.parse_args()


input_ctm=args.input_ctm
output_ctm=args.output_ctm

class Segment:
	def __init__(self, line):
		tok=line.strip().split(' ')
		assert len(tok) == 5, 'Line should have exactly 5 tokens in CTM file:\n|{}|'.format(line.strip())
		self.file=tok[0]
		self.channel=tok[1]
		self.start=float(tok[2])
		self.dur=float(tok[3])
		self.text=tok[4]

	def __str__(self):
		return '{} {} {} {} {}'.format(self.file,self.channel,self.start,self.dur,self.text)

segments=[]

with open(input_ctm) as f:
	for line in f:
		seg=Segment(line)
		if seg.text != "<UNK>" and seg.text[:3]!="spn" and seg.text[:3]!="sil":
			segments.append(seg)

segments=sorted(segments,key=lambda segment: segment.start)

first=segments[0]
new_segments=[]
for second in segments[1:]:
	if first.start + first.dur - second.start > 0.01:
		if first.text == second.text:
			first.dur=second.start+second.dur-first.start
			second=None
		else:
			print 'Cannot fix segments: {} vs {}'.format(first,second)
			second=None

	if second:
		new_segments.append(first)
		first=second

if second:
	new_segments.append(second)

with open(output_ctm,'w') as f:
	for segment in new_segments:
		f.write(str(segment)+'\n')