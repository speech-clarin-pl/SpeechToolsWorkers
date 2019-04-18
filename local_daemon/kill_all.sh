#!/usr/bin/env bash

for p in PID/* ; do
	fuser -k $p
done