#!/bin/bash

set -e -o pipefail

data_path=/data
dist_path=/dist

echo "$0 $@" # Print the command line for logging
. parse_options.sh || exit 1

if [ $# -ne 2 ]; then
  echo "Usage: ./local/train_g2p.sh <lexicon> <model_out>"
  exit 1
fi

if [ -f "$1" ]; then
  lexicon=$(readlink -f $1)
  model=$(readlink -f $2)
else
  #else it's within the $data_path
  lexicon=$data_path/$1
  model=$data_path/$2
fi

ln -s $dist_path/path.sh path.sh

. path.sh

export LD_LIBRARY_PATH=$KALDI_ROOT/tools/openfst/lib

python2.7 $KALDI_ROOT/tools/phonetisaurus-g2p/src/scripts/phonetisaurus-train --lexicon $lexicon --seq2_del

mv train/model.fst "$model"
