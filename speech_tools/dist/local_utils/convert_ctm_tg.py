from textgrid import TextGrid,IntervalTier
import argparse
import os
import os.path

def convert_ctm_to_textgrid(ctms,textgrid):
	for ctm in ctms:
		tiername=os.path.splitext(ctm)[0]
		ret=[]
		with open(ctm) as f:
			for l in f:
				tok=l.split(' ')
				word=tok[4].strip()
				beg=float(tok[2])
				dur=float(tok[3])
				ret.append((word,beg,dur))
		t=IntervalTier(name=tiername)
		for seg in ret:
			try:
					t.add(round(seg[1],2),round(seg[1]+seg[2],2),seg[0])
			except ValueError:
					print("Error in seg: "+seg[0])
		tg=TextGrid()
		tg.append(t)
		with open(textgrid,'w') as f:
			tg.write(f)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Converts CTM to TextGrid')
	parser.add_argument('ctm', help='CTM file(s)', nargs='+')
	parser.add_argument('tg', help='TextGrid')

	args = parser.parse_args()
	
	convert_ctm_to_textgrid(args.ctm,args.tg)
