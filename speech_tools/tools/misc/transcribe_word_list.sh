#!/bin/bash

set -e -o pipefail

data_path=/data
dist_path=/dist
model_path=/dist/model/default/phonetisaurus

echo "$0 $@" # Print the command line for logging
. parse_options.sh || exit 1

if [ $# -ne 2 ]; then
  echo "Usage: ./local/transcribe_word_list.sh <word_list> <lexicon>"
  exit 1
fi

if [ -f "$1" ]; then
  word_list=$(readlink -f $1)
  lexicon=$(readlink -f $2)
else
  #else it's within the $data_path
  word_list=$data_path/$1
  lexicon=$data_path/$2
fi

ln -s $dist_path/path.sh

. path.sh

export LD_LIBRARY_PATH=$KALDI_ROOT/tools/openfst/lib
python2.7 $KALDI_ROOT/tools/phonetisaurus-g2p/src/scripts/phonetisaurus-apply --model $model_path/model.fst --lexicon $model_path/lexicon.txt --word_list $word_list -p 0.8 >$lexicon
