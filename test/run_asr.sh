#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:studio "/tools/Recognize/run.sh test.wav trans.txt"
