FROM resin/raspberrypi2-python:3.5.1

COPY setup.sh .
COPY requirements.txt .
COPY test-requirements.txt .

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    &&  apt-get --yes install \
            lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/{apt,dpkg,cache,log}

RUN bash setup.sh && \
    rm -f setup.sh requirements.txt test-requirements.txt