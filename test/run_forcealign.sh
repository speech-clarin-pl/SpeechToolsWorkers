#!/usr/bin/env bash

docker run --rm -v ${PWD}/work:/data -v model:/dist/model/default danijel3/clarin-pl-speechtools "/tools/ForcedAlign/run.sh test.wav trans.txt ali.ctm"
