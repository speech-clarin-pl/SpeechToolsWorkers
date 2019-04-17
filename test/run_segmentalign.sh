#!/usr/bin/env bash

docker run --rm -it -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:pkf "/tools/SegmentAlign/run.sh pkf.wav pkf.txt pkf.ctm"
