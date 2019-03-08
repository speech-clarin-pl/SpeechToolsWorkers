#!/bin/bash

set -e -o pipefail

dist_path=/dist
tmp_path=/tmp/work
data_path=/data
nj=1

model_name=default

beam=20
retry_beam=300

echo "$0 $@"  # Print the command line for logging
. parse_options.sh || exit 1;

if [ $# -ne 4 ]; then
  echo "Usage: ./run.sh <input-wav> <seg-txt> <spk_ctm> <out-ctm>"
  echo ""
  echo "Options:"
  echo "    --model_name"
  echo "    --beam"
  echo "    --retry_beam"
  exit 1
fi

#if file is an existing global path
if [ -f "$1" ] ; then
    wav_file=$(readlink -f $1)
    txt_file=$(readlink -f $2)
    spk_ctm=$(readlink -f $3)
    out=$(readlink -f $4)
else
    #else it's within the $data_path
    wav_file=$data_path/$1
    txt_file=$data_path/$2
    spk_ctm=$data_path/$3
    out=$data_path/$4
fi

for f in $wav_file $txt_file $spk_ctm; do
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
ln -s ${dist_path}/model/${model_name}/tri3b_mmi
ln -s ${dist_path}/model/${model_name}/phonetisaurus

. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps
ln -s $KALDI_ROOT/egs/wsj/s5/conf
ln -s $KALDI_ROOT/egs/wsj/s5/local


mkdir data

echo input $wav_file > ${tmp_path}/data/wav.scp
echo "input input A" > ${tmp_path}/data/reco2file_and_channel
awk '{printf "seg_%s_%03d input %0.2f %0.2f\n", $5, NR, $3, $3+$4}' < $spk_ctm > ${tmp_path}/data/segments
awk '{printf "seg_%s_%03d spk_%s\n", $5, NR, $5}' < $spk_ctm > ${tmp_path}/data/utt2spk
./utils/utt2spk_to_spk2utt.pl < ${tmp_path}/data/utt2spk > ${tmp_path}/data/spk2utt
cut -f1 -d' ' ${tmp_path}/data/utt2spk > ${tmp_path}/data/utt.id
paste -d ' ' ${tmp_path}/data/utt.id ${txt_file} > ${tmp_path}/data/text

for f in ${tmp_path}/data/* ; do
	sort -o $f $f
done




./steps/make_mfcc.sh --nj $nj data
./steps/compute_cmvn_stats.sh data
./local_utils/prepare_dict.sh data dict
./utils/prepare_lang.sh dict "<unk>" tmp lang
./steps/align_fmllr.sh --nj $nj --beam ${beam} --retry-beam ${retry_beam} data lang tri3b_mmi ali
./steps/get_train_ctm.sh data lang ali
./local_utils/get_phoneme_ctm.sh data lang ali

awk '$0="@"$0' ali/phonectm | cat ali/ctm - | sort -r -k3n > $out

echo Finished generating alignment...

echo "Cleaning up..."
rm -rf ${tmp_path}
