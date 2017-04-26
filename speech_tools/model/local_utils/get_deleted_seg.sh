#!/bin/bash

#After doing the ./steps/cleanup/clean_and_segment_data.sh, this script takes the
#debug output of one of the scripts (ctm_edits.segmented) and generates a small data dir
#containing the segments that were deleted in the cleanup stage.

set -e -o pipefail

padding=0.02

echo "$0 $@"  # Print the command line for logging

[ -f ./path.sh ] && . ./path.sh
. parse_options.sh || exit 1;

if [ $# -ne 5 ]; then
  echo "Usage: $0 [options] <cleanup-dir> <lang> <data-dir> <ctm-cleaned> <deleted-data-dir>"
  echo "e.g.:"
  echo "$0 exp/cleanup data/lang data/train exp/ali_clean/ctm data/deleted"
  exit 1;
fi

cleanup=$1
lang=$2
data=$3
ctm_clean=$4
deldata=$5

# ctm_seg_out=${cleanup}/ctm_edits.segmented

# for f in $cleanup/{text.del,segments.del} ; do
# 	rm -f $f
# done

#version 1 - prints only that which was marked in "ctm_edits.segmented" as deleted

# grep "start-deleted-segment" $ctm_seg_out | \
# sed "s/.*start-deleted-segment-\([0-9]*\)\[start=\([0-9]*\),end=\([0-9]*\),.*/\1 \2 \3/" | \
# 	while read seg_id start_seg end_seg ; do 

# 		first=`sed -n "${start_seg}p" $ctm_seg_out`
# 		last=`sed -n "${end_seg}p" $ctm_seg_out`

# 		file_id=`echo $first | cut -f 1 -d '['`

# 		text=`sed -n "${start_seg},${end_seg}p" $ctm_seg_out | \
# 		 awk '{print $7}' | grep -v "<eps>" | tr '\n' ' '`

# 		echo ${file_id}-${seg_id} $text >> $cleanup/text.del

# 		start_time=`echo $first | awk '{print $3}'`
# 		end_start=`echo $last | awk '{print $3}'`
# 		end_len=`echo $last | awk '{print $4}'`
# 		end_time=`echo "${end_start}+${end_len}" | bc`

# 		echo ${file_id}-${seg_id} $file_id $start_time $end_time >> $cleanup/segments.del
# 	done

#version 2 - gets everything that is (!)not between start/end clean segment

# text=''

# cat $ctm_seg_out | awk '/end-segment.*start-deleted-segment/{f=1} /start-segment/{f=0} f' |
# while read line ; do
# 	if `echo $line | grep -q "start-deleted-segment"` ; then

# 		if [ -n "$text" ] ; then
# 			echo ${file_id}-${seg_id} $text	>> $cleanup/text.del

# 			end_start=`echo $line | awk '{print $3}'`
# 			end_len=`echo $line | awk '{print $4}'`
# 			end_time=`echo "${end_start}+${end_len}" | bc`

# 			echo ${file_id}-${seg_id} $file_id $start_time $end_time >> $cleanup/segments.del
# 		fi

# 		seg_id=`echo $line | sed "s/.*start-deleted-segment-\([0-9]*\).*/\1/"`
# 		file_id=`echo $line | cut -f 1 -d '['`
# 		text=''
# 	else
		
# 		if [ -z "$text" ] ; then
# 			start_time=`echo $line | awk '{print $3}'`
# 		fi

#  		word=`echo $line | awk '{print $7}'`
#  		if [ "$word" != "<eps>" ] ; then
#  			text="$text $word"
#  		fi
#  	fi
#  done 

#final version - this generates the text by comparing output of cleaning to original

oov=$(cat $lang/oov.int)

python local_utils/get_text_from_segments.py $cleanup/text $cleanup/segments /dev/stdout | \
align-text ark:- ark:$data/text ark,t:- | \
steps/cleanup/internal/get_ctm_edits.py --oov=$oov --symbol-table=$lang/words.txt \
	/dev/stdin $ctm_clean $cleanup/ctm_edits_del

python local_utils/extract_deleted.py $cleanup/ctm_edits_del $cleanup/text.del $cleanup/segments.del

sort -o $cleanup/text.del $cleanup/text.del
sort -o $cleanup/segments.del $cleanup/segments.del

utils/data/subsegment_data_dir.sh --segment-end-padding $padding ${data} $cleanup/segments.del $cleanup/text.del $deldata
steps/compute_cmvn_stats.sh $deldata

