#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data clarinpl/speech-tools:studio "/tools/Recognize/run.sh test.wav trans.txt"
