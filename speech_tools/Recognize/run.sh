#!/bin/bash

set -e -o pipefail

echo "$0 $@"  # Print the command line for logging
. parse_options.sh || exit 1;

if [ $# -ne 2 ]; then
  echo "Usage: ./run.sh <input-wav> <proj-name>"
  exit 1
fi

wav_file=`readlink -f $1`
proj_name=$2

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -e $proj_name ] ; then
	mkdir -p ${proj_name}
fi

mkdir ${proj_name}/data

echo input $wav_file > ${proj_name}/data/wav.scp
echo input unknown > ${proj_name}/data/text
echo input spk > ${proj_name}/data/utt2spk
echo spk input > ${proj_name}/data/spk2utt

cd ${proj_name}

ln -s ${SCRIPT_DIR}/model/path.sh
ln -s ${SCRIPT_DIR}/model/extractor
ln -s ${SCRIPT_DIR}/model/local_utils
ln -s ${SCRIPT_DIR}/model/chain/tree
ln -s ${SCRIPT_DIR}/model/lang_carpa
ln -s ${SCRIPT_DIR}/model/lang_test

mkdir tdnn
for f in ${SCRIPT_DIR}/model/chain/tdnn/* ; do ln -s `readlink -f $f` tdnn/`basename $f` ; done

. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps
ln -s $KALDI_ROOT/egs/wsj/s5/conf
ln -s $KALDI_ROOT/egs/wsj/s5/local

./steps/make_mfcc.sh --nj 1 --mfcc-config conf/mfcc_hires.conf data
./steps/compute_cmvn_stats.sh data
./steps/online/nnet2/extract_ivectors_online.sh --nj 1 data extractor ivectors
./steps/nnet3/decode.sh --acwt 1.0 --post-decode-acwt 10.0 --frames-per-chunk 140 --nj 1 --num-threads 4 --online-ivector-dir ivectors --skip-scoring true tree/graph data tdnn/decode
./steps/lmrescore_const_arpa.sh --skip-scoring true lang_test lang_carpa data tdnn/decode tdnn/decode_rs

lattice-best-path --lm-scale=12 "ark:gunzip -c tdnn/decode_rs/lat.*.gz|" ark,t:- | ./utils/int2sym.pl -f 2- tree/graph/words.txt | cut -f2- -d' '  > output.txt

echo Finished recognizing...
