#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:sejm "/tools/KeywordSpotting/run.sh sejm.wav keywords.txt sejm.kws"
