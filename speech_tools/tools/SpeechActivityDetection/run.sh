#!/bin/bash

set -e -o pipefail

dist_path=/dist
tmp_path=/tmp/work
data_path=/data

nj=1

echo "$0 $@"  # Print the command line for logging
. parse_options.sh || exit 1;

if [ $# -ne 2 ]; then
  echo "Usage: ./run.sh <input-wav> <out-ctm>"
  echo ""
  echo "Options:"
  exit 1
fi

#if file is an existing global path
if [ -f "$1" ] ; then
    wav_file=$(readlink -f $1)
    out=$(readlink -f $2)
else
    #else it's within the $data_path
    wav_file=$data_path/$1
    out=$data_path/$2
fi

for f in $wav_file; do
  [ ! -f "$f" ] && echo "no such file $f" && exit 1;
done

if [ -e "$tmp_path" ] ; then
	rm -rf ${tmp_path}
fi

mkdir -p ${tmp_path}
mkdir ${tmp_path}/data

tmp_wav_file=${tmp_path}/$(basename $wav_file)
sox $wav_file -r8k $tmp_wav_file

echo input $tmp_wav_file > ${tmp_path}/data/wav.scp
echo "input n/a" > ${tmp_path}/data/text
echo input spk > ${tmp_path}/data/utt2spk
echo spk input > ${tmp_path}/data/spk2utt

cd ${tmp_path}

ln -s ${dist_path}/path.sh
ln -s ${dist_path}/sad/conf
ln -s ${dist_path}/sad/segmentation_1a/tdnn_stats_asr_sad_1a model

. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps

./steps/segmentation/detect_speech_activity.sh --nj $nj --cmd run.pl --extra-left-context 79 --extra-right-context 21 \
    --extra-left-context-initial 0 --extra-right-context-final 0 --frames-per-chunk 150 \
    --mfcc-config conf/mfcc_hires.conf \
    data model mfcc work sad

awk '{printf "input 1 %0.3f %0.3f speech\n",$3,$4-$3}' < sad_seg/segments > $out

echo Finished generating speech activity segmentation...
