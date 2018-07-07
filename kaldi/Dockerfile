FROM debian:8
MAINTAINER Danijel Koržinek <danijel@pja.edu.pl>

RUN apt-get update && \
            apt-get install -y g++ zlib1g-dev make automake libtool-bin git autoconf && \
            apt-get install -y subversion libatlas3-base bzip2 wget python2.7 python3 python3-pip && \
            apt-get clean && apt-get autoclean && rm -rf /var/lib/apt/lists/* && \
            ln -s -f bash /bin/sh

RUN git clone https://github.com/kaldi-asr/kaldi /kaldi

RUN cd /kaldi/tools && make  && ./extras/install_phonetisaurus.sh && find -name *.o -delete

RUN cd /kaldi/src && ./configure --shared && make -j4 depend && make -j4 && find -name *.o -delete

ENTRYPOINT ["/bin/sh"]