FROM resin/raspberrypi2-python:3.5.1

COPY setup.sh .
COPY requirements.txt .
COPY test-requirements.txt .

RUN bash setup.sh && \
    rm -f setup.sh requirements.txt test-requirements.txt
