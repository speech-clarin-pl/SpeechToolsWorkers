#!/usr/bin/env bash

(cd $(dirname "${BASH_SOURCE[0]}")/..
for w in `seq 1 20` ; do
	python3.7 -m worker.run_daemon -u www-data -g www-data -l local_daemon/logs/worker$w.log -p local_daemon/PID/worker$w.pid -d
done
)