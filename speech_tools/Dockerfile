FROM debian:10

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        g++ \
        make \
        automake \
        autoconf \
        bzip2 \
        unzip \
        wget \
        sox \
        libtool \
        git \
        subversion \
        python2.7 \
        python3 \
        zlib1g-dev \
        ca-certificates \
        gfortran \
        patch \
        ffmpeg \
        python-dev \
        python3-pip \
        python3-setuptools \
        autoconf-archive\
	    vim && \
        rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi #EOL
RUN cd /opt/kaldi/tools && \
       ./extras/install_mkl.sh && \
       make && \
       ./extras/install_phonetisaurus.sh && \
       cd /opt/kaldi/src && \
       ./configure --shared && \
       make depend -j 8 && \
       make -j 8 && \
       cd /opt && git clone https://github.com/mitlm/mitlm.git && cd mitlm && ./autogen.sh && make && make install && \
       find /opt/kaldi -type f \( -name "*.o" -o -name "*.la" -o -name "*.a" \) -exec rm {} \; && \
       find /opt/intel -type f -name "*.a" -exec rm {} \; && \
       find /opt/intel -type f -regex '.*\(_mc.?\|_mic\|_thread\|_ilp64\)\.so' -exec rm {} \; && \
       rm -rf /opt/kaldi/.git

RUN ln -sf /usr/bin/python3 /usr/bin/python && python3 -m pip install -U pip && python3 -m pip install textgrid pympi-ling

COPY dist /dist

COPY tools /tools

COPY parse_options.sh /tools

WORKDIR /tools

ENTRYPOINT ["/bin/bash","-c"]
