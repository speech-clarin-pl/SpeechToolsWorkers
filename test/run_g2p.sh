#!/usr/bin/env bash

docker run -it --rm -v ${PWD}/work:/data danijel3/clarin-pl-speechtools:studio "/tools/misc/transcribe_word_list.sh keywords.txt lexicon.txt"
