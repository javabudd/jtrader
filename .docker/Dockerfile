FROM python:3.6-alpine

MAINTAINER Andres OBrien <oban0601@gmail.com>

ENV PS1="\[\e[0;33m\]|> jtrader <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

RUN apk update && \
    apk add \
    automake \
    make \
    gcc \
    g++ \
    hdf5-dev \
    jpeg-dev \
    openblas-dev

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install -r requirements.txt

COPY . /src

RUN python setup.py install

WORKDIR /

CMD ["jtrader", "-d", "start-worker"]
