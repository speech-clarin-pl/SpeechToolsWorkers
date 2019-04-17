#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:studio "/kaldi/src/bin/compute-wer ark:/data/test.txt ark:/data/trans.txt" > ${PWD}/work/wer.txt

cat ${PWD}/work/wer.txt