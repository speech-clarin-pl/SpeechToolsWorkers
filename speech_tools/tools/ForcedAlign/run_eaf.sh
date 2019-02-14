#!/bin/bash

set -e -o pipefail

dist_path=/dist
tmp_path=/tmp/work
data_path=/data
nj=1
spk_tier=true
skip_tiers=
phones=true

model_name=default

beam=20
retry_beam=300

echo "$0 $@"  # Print the command line for logging
. parse_options.sh || exit 1;

if [ $# -ne 3 ]; then
  echo "Usage: ./run_eaf.sh <input-wav> <input-eaf> <out-eaf>"
  echo ""
  echo "Options:"
  echo "    --model_name"
  echo "    --beam"
  echo "    --retry_beam"
  echo "    --nj"
  echo "    --spk-tier"
  echo "    --skip-tiers"
  echo "    --phones"
  exit 1
fi

#if file is an existing global path
if [ -f "$1" ] ; then
    wav_file=$(readlink -f $1)
    eaf_in=$(readlink -f $2)
    eaf_out=$(readlink -f $3)
else
    #else it's within the $data_path
    wav_file=$data_path/$1
    eaf_in=$data_path/$2
    eaf_out=$data_path/$3
fi

for f in $wav_file $eaf_in; do
  [ ! -f "$f" ] && echo "no such file $f" && exit 1;
done

[ ! -d "${dist_path}/model/${model_name}" ] &&  echo "need to get the proper model: ${model_name}" && exit 1;

if [ -e "$tmp_path" ] ; then
	rm -rf ${tmp_path}
fi

mkdir -p ${tmp_path}
mkdir ${tmp_path}/data

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

echo input $wav_file > data/wav.scp
echo "input input A" > data/reco2file_and_channel

if $spk_tier ; then
    python3 local_utils/eaf2data.py --spk-tier --skip-tiers "$skip_tiers" $eaf_in data
else
    python3 local_utils/eaf2data.py --skip-tiers "$skip_tiers" $eaf_in data
fi

for f in data/* ; do
    sort -o $f $f
done

./utils/utt2spk_to_spk2utt.pl data/utt2spk > data/spk2utt


./steps/make_mfcc.sh --nj $nj data
./steps/compute_cmvn_stats.sh data
./local_utils/prepare_dict.sh data dict
./utils/prepare_lang.sh dict "<unk>" tmp lang
./steps/align_fmllr.sh --nj $nj --beam ${beam} --retry-beam ${retry_beam} data lang tri3b_mmi ali
./steps/get_train_ctm.sh --use-segments false data lang ali

if $phones ; then
    ./local_utils/get_phoneme_ctm.sh --use-segments false data lang ali

    python3 local_utils/ctm2eaf.py --phones-ctm ali/phonectm ali/ctm data/seg2tier ${eaf_in} ${eaf_out}
else
    python3 local_utils/ctm2eaf.py ali/ctm data/seg2tier ${eaf_in} ${eaf_out}
fi

echo Finished generating alignment...

echo "Cleaning up..."
rm -rf ${tmp_path}
