#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:studio "/tools/SpeakerDiarization/run.sh switchboard.wav spk.ctm"
