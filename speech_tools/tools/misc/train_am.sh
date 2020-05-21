#!/bin/bash

set -e -o pipefail

data_path=/data
dist_path=/dist
tmp_path=/tmp/work

model_name=default

beam=20
retry_beam=300

echo "$0 $@" # Print the command line for logging
. parse_options.sh || exit 1

if [ $# -ne 2 ]; then
  echo "Usage: ./local/train_am.sh <corpus> <model_out>"
  echo ""
  echo "Options:"
  echo "    --model_name"
  echo "    --beam"
  echo "    --retry_beam"
  exit 1
fi

if [ -d "$1" ]; then
  corpus=$(readlink -f $1)
  out=$(readlink -f $2)
else
  #else it's within the $data_path
  corpus=$data_path/$1
  out=$data_path/$2
fi

echo "Processing $corpus to $out"

[ ! -d "${dist_path}/model/${model_name}" ] && echo "need to get the proper model: ${model_name}" && exit 1

if [ -e "$tmp_path" ]; then
  rm -rf ${tmp_path}
fi

mkdir -p ${tmp_path}
mkdir ${tmp_path}/data

for wav_file in $corpus/*.wav; do
  wav_id=$(basename "$wav_file" .wav)

  txt_file=${wav_file%wav}txt
  [ ! -f "$txt_file" ] && echo "Missing $txt_file" && exit 1

  spk_file=${wav_file%wav}spk
  spk=$wav_id
  [ -f "$spk_file" ] && spk=$(head -n 1 "$spk_file" | cut -f1 -d' ')

  wav_id=${spk}_${wav_id}

  echo "$wav_id $wav_file" >>${tmp_path}/data/wav.scp
  echo "$wav_id $spk" >>${tmp_path}/data/utt2spk
  echo "$wav_id $(cat "$txt_file" | tr '\n' ' ')" >>${tmp_path}/data/text
done

cd ${tmp_path}

for f in data/*; do
  sort -o $f $f
done

ln -s ${dist_path}/path.sh
ln -s ${dist_path}/local_utils
ln -s ${dist_path}/model/${model_name}/tri3b_mmi
ln -s ${dist_path}/model/${model_name}/phonetisaurus

. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps
ln -s $KALDI_ROOT/egs/wsj/s5/conf
ln -s $KALDI_ROOT/egs/wsj/s5/local

./utils/utt2spk_to_spk2utt.pl <data/utt2spk >data/spk2utt
./steps/make_mfcc.sh --nj 1 data
./steps/compute_cmvn_stats.sh data
./local_utils/prepare_dict.sh data dict
./utils/prepare_lang.sh dict "<unk>" tmp lang
./steps/align_fmllr.sh --nj 1 --beam ${beam} --retry-beam ${retry_beam} data lang tri3b_mmi ali

./steps/train_sat.sh 2500 15000 data lang ali $out

echo "Cleaning up..."
rm -rf ${tmp_path}
