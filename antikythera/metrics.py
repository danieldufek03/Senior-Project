#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Analysis of the recieved packets.

"""
import logging

from random import random
from time import sleep
from queue import Queue, Empty

_logger = logging.getLogger(__name__)


def metrics(process_id, q):
    """ Perform analyasis of the packets.

    """
    _logger.info("Metrics: worker process {} started".format(process_id))

    while True:
        try:
            p = q.get(timeout=10)
            _logger.trace("Metrics: Process {} consumed packet {} Queue size is now {}".format(process_id, p['gsmtap'].frame_nr, q.qsize()))
            sleep(1)
        except Empty:
            _logger.info("Metrics: Process {} Queue empty".format(process_id))
            sleep(1)

if __name__ == "__main__":
    metrics()
