#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:studio "/tools/SpeechActivityDetection/run.sh switchboard.wav vad.ctm"

docker run --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:studio "python /dist/local_utils/convert_ctm_tg.py /data/vad.ctm /data/vad.TextGrid"
