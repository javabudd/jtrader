FROM python:3.8

MAINTAINER Andres OBrien <oban0601@gmail.com>

ENV PS1="\[\e[0;33m\]|> jtrader <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "
ENV NPY_NUM_BUILD_JOBS=4

RUN apt update && \
    apt -y install \
    automake \
    ccache \
    make \
    gcc \
    g++ \
    gfortran \
    libhdf5-dev \
    libjpeg-dev \
    libatlas-base-dev \
    liblapack-dev \
    libgmp-dev \
    libxml2-dev \
    libmpfr-dev \
    libmpc-dev \
    libsuitesparse-dev \
    libopenblas-dev \
    python3-dev

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

WORKDIR /src

RUN pip install --upgrade pip setuptools wheel

COPY ./requirements.txt /src/requirements.txt

RUN pip install -r requirements.txt

COPY . /src

RUN find / -name '*.pyc' -delete && python setup.py install

WORKDIR /

CMD ["jtrader", "-d", "start-worker"]
