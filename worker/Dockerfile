FROM danijel3/clarin-pl-speechtools:studio
MAINTAINER Danijel Koržinek <danijel@pja.edu.pl>

RUN apt-get update && apt-get -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev && \
	apt-get clean

RUN wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz && \
		tar xf Python-3.7.3.tar.xz && cd Python-3.7.3 && \
		./configure && make && make altinstall && \
		cd / && rm -rf /Python-3.7.3

RUN mkdir /worker

COPY requirements.txt /worker/requirements.txt

RUN python3.7 -m pip install -r /worker/requirements.txt

COPY __main__.py /worker/__main__.py
COPY __init__.py /worker/__init__.py
COPY config.py /worker/config.py
COPY worker.py /worker/worker.py
COPY tasks /worker/tasks

WORKDIR /
ENTRYPOINT ["python3.7","-m","worker"]

