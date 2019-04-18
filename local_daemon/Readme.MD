# Local daemon scripts

This folder contains scripts for running the workers as local daemons. If you prefer to run everything locally, 
without docker, you need to install all the pre-requisites (mongo, rabbitmq, packages from requirements.txt, etc) 
and use these scripts to run the workers as regular daemon processes.

The folder contains subfolders logs for containing log files for individual workers and PID for PID files
that can be monitored and controlled using the fuser program.  