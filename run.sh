for w in `seq 1 20` ; do 
	python run.py -u www-data -g www-data -l logs/worker$w.log -p PID/worker$w.pid -d
done

