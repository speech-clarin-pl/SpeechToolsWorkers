FROM clarinpl/speech-tools
MAINTAINER Danijel Koržinek <danijel@pja.edu.pl>

COPY --from=clarinpl/speech-models:studio /models/studio /dist/model/studio
RUN ln -s /dist/model/studio /dist/model/default
RUN ln -s /tools/parse_options.sh /parse_options.sh

RUN mkdir /worker

COPY requirements.txt /worker/requirements.txt

RUN python3 -m pip install -r /worker/requirements.txt

COPY __main__.py /worker/__main__.py
COPY __init__.py /worker/__init__.py
COPY config.py /worker/config.py
COPY worker.py /worker/worker.py
COPY tasks /worker/tasks

WORKDIR /
ENTRYPOINT ["python3","-m","worker"]