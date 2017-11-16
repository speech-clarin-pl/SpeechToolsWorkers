#!/bin/bash

set -e -o pipefail

beam=20
retry_beam=300

echo "$0 $@"  # Print the command line for logging
. parse_options.sh || exit 1;

if [ $# -ne 3 ]; then
  echo "Usage: ./run.sh <input-wav> <input-txt> <proj-name>"
  echo "Creates a folder <proj-name> and aligns the WAV/TXT inside it."
  echo "Result is saved in <proj-name>/output.ctm"
  exit 1
fi

wav_file=`readlink -f $1`
txt_file=`readlink -f $2`
proj_name=`readlink -f $3`

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -e $proj_name ] ; then
    mkdir -p ${proj_name}
fi

mkdir ${proj_name}/data

echo input $wav_file > ${proj_name}/data/wav.scp
echo input `cat $txt_file` > ${proj_name}/data/text
echo input spk > ${proj_name}/data/utt2spk
echo spk input > ${proj_name}/data/spk2utt

cd ${proj_name}

ln -s ${SCRIPT_DIR}/model/path.sh
ln -s ${SCRIPT_DIR}/model/tri3b_mmi
ln -s ${SCRIPT_DIR}/model/local_utils
ln -s ${SCRIPT_DIR}/model/phonetisaurus


. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps
ln -s $KALDI_ROOT/egs/wsj/s5/conf
ln -s $KALDI_ROOT/egs/wsj/s5/local

./steps/make_mfcc.sh --nj 1 data
./steps/compute_cmvn_stats.sh data
./local_utils/prepare_dict.sh data dict
./utils/prepare_lang.sh dict "<unk>" tmp lang
./steps/align_fmllr.sh --nj 1 --beam ${beam} --retry-beam ${retry_beam} data lang tri3b_mmi ali
./steps/get_train_ctm.sh data lang ali
./local_utils/get_phoneme_ctm.sh data lang ali

awk '$0="@"$0' ali/phonectm | cat ali/ctm - | sort -r -k3n > output.ctm

echo Finished generating alignment...
