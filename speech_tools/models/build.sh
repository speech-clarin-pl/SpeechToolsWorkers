#!/usr/bin/env bash

for f in Dockerfile.* ; do 
	docker build -t danijel3/clarin-pl-speechtools:${f#Dockerfile.} -f $f .
done
