#!/bin/bash

wav=`basename $1`
text=`basename $2`

wav_id=`printf "use clarin\ndb.resources.find({file:'$wav'},{_id:1})"|mongo --quiet|head -n2|tail -n1|cut -f4 -d'"'`
text_id=`printf "use clarin\ndb.resources.find({file:'$text'},{_id:1})"|mongo --quiet|head -n2|tail -n1|cut -f4 -d'"'`

printf "http://mowa.clarin-pl.eu/tools/ui/multiview/$wav_id/$text_id\n"
