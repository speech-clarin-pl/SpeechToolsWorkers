FROM kaldiasr/kaldi 

RUN apt-get update && \
    apt-get install -y bc python3 python2.7 python3-pip python-dev && \
    apt-get clean && apt-get autoclean && rm -rf /var/lib/apt/lists/*

RUN pip3 install textgrid pympi-ling

RUN cd /opt/kaldi/tools && ./extras/install_phonetisaurus.sh

COPY dist /dist

COPY tools /tools

COPY parse_options.sh /tools

WORKDIR /tools

ENTRYPOINT ["/bin/bash","-c"]
