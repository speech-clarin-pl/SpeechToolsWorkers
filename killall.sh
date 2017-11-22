for p in PID/* ; do
	fuser -k $p
done
