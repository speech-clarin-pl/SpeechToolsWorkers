#!/bin/bash

set -e -o pipefail

dist_path=/dist
tmp_path=/tmp/work
data_path=/data

nj=1
nj_xvector=1
threshold=0

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
mkdir ${tmp_path}/exp

tmp_wav_file=${tmp_path}/$(basename $wav_file).wav
sox $wav_file -r8k $tmp_wav_file

echo input $tmp_wav_file > ${tmp_path}/data/wav.scp
echo "input n/a" > ${tmp_path}/data/text
echo input spk > ${tmp_path}/data/utt2spk
echo spk input > ${tmp_path}/data/spk2utt


cd ${tmp_path}

ln -s ${dist_path}/path.sh
ln -s ${dist_path}/diarization/conf
ln -s ${dist_path}/diarization/xvector_nnet_1a model
ln -s ${dist_path}/sad/conf conf_sad
ln -s ${dist_path}/sad/segmentation_1a/tdnn_stats_asr_sad_1a model_sad

. path.sh

ln -s $KALDI_ROOT/egs/wsj/s5/utils
ln -s $KALDI_ROOT/egs/wsj/s5/steps
ln -s $KALDI_ROOT/egs/callhome_diarization/v2/diarization
ln -s $KALDI_ROOT/egs/callhome_diarization/v2/local


./steps/make_mfcc.sh --mfcc-config conf/mfcc.conf --nj $nj --write-utt2num-frames true data

./local/nnet3/xvector/prepare_feats.sh --nj $nj data data_cmn dia_cmn

./steps/segmentation/detect_speech_activity.sh --nj $nj --cmd run.pl --extra-left-context 79 --extra-right-context 21 \
    --extra-left-context-initial 0 --extra-right-context-final 0 --frames-per-chunk 150 \
    --mfcc-config conf_sad/mfcc_hires.conf \
    data_cmn model_sad mfcc_sad work_sad sad

./utils/data/subsegment_data_dir.sh data_cmn sad_seg/segments data_segmented

./diarization/nnet3/xvector/extract_xvectors.sh --nj $nj_xvector --window 1.5 --period 0.75 --apply-cmn false  --min-segment 0.5 model data_segmented xvectors

#TODO check callhome1 vs callhome2
./diarization/nnet3/xvector/score_plda.sh --nj $nj_xvector model/xvectors_callhome2 xvectors plda_scores

./diarization/cluster.sh --nj $nj --threshold $threshold plda_scores plda_cluster

awk '{printf "%s %s %0.3f %0.3f %s\n",$2,$3,$4,$5,$8}' < plda_cluster/rttm > $out

echo Finished generating speaker diarization...
