#!/bin/bash

set -e -o pipefail

dist_path=/dist
tmp_path=/tmp/work
data_path=/data
nj=1

model_name=default

echo "$0 $@"  # Print the command line for logging
. parse_options.sh || exit 1;

if [ $# -ne 3 ]; then
  echo "Usage: ./run.sh <input-wav> <diar-ctm> <out-txt>"
  echo ""
  echo "Options:"
  echo "    --model_name"
  exit 1
fi

#if file is an existing global path
if [ -f "$1" ] ; then
    wav_file=$(readlink -f $1)
    spk_ctm=$(readlink -f $2)
    out=$(readlink -f $3)
else
    #else it's within the $data_path
    wav_file=$data_path/$1
    spk_ctm=$data_path/$2
    out=$data_path/$3
fi

for f in $wav_file $spk_ctm; do
  [ ! -f "$f" ] && echo "no such file $f" && exit 1;
done

[ ! -d "${dist_path}/model/${model_name}" ] &&  echo "need to get the proper model: ${model_name}" && exit 1;


if [ -e "$tmp_path" ] ; then
	rm -rf ${tmp_path}
fi

mkdir -p ${tmp_path}

cd ${tmp_path}

ln -s ${dist_path}/path.sh
ln -s ${dist_path}/local_utils
ln -s ${dist_path}/model/${model_name}/extractor
ln -s ${dist_path}/model/${model_name}/chain/tree
ln -s ${dist_path}/model/${model_name}/lang_carpa
ln -s ${dist_path}/model/${model_name}/lang_test

mkdir tdnn
for f in ${dist_path}/model/${model_name}/chain/tdnn/* ; do ln -s $(readlink -f $f) tdnn/$(basename $f) ; done

. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps
ln -s $KALDI_ROOT/egs/wsj/s5/conf
ln -s $KALDI_ROOT/egs/wsj/s5/local

mkdir data

echo input $wav_file > ${tmp_path}/data/wav.scp
awk '{printf "seg_%s_%03d input %0.2f %0.2f\n", $5, NR, $3, $3+$4}' < $spk_ctm > ${tmp_path}/data/segments
awk '{printf "seg_%s_%03d unknown\n", $5, NR}' < $spk_ctm > ${tmp_path}/data/text
awk '{printf "seg_%s_%03d spk_%s\n", $5, NR, $5}' < $spk_ctm > ${tmp_path}/data/utt2spk
./utils/utt2spk_to_spk2utt.pl < ${tmp_path}/data/utt2spk > ${tmp_path}/data/spk2utt

for f in ${tmp_path}/data/* ; do
	sort -o $f $f
done

./steps/make_mfcc.sh --nj $nj --mfcc-config conf/mfcc_hires.conf data
./steps/compute_cmvn_stats.sh data
./steps/online/nnet2/extract_ivectors_online.sh --nj $nj data extractor ivectors
./steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 --frames-per-chunk 140 --nj $nj --num-threads 4 --online-ivector-dir ivectors --skip-scoring true tree/graph data tdnn/decode
./steps/lmrescore_const_arpa.sh --skip-scoring true lang_test lang_carpa data tdnn/decode tdnn/decode_rs

lattice-best-path --lm-scale=12 "ark:gunzip -c tdnn/decode_rs/lat.*.gz|" ark,t:- | ./utils/int2sym.pl -f 2- tree/graph/words.txt | cut -f2- -d' '  > $out

echo Finished recognizing...

echo "Cleaning up..."
rm -rf ${tmp_path}