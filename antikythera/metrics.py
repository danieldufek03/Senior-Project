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


def metrics(thread_id, q):
    """ Perform analyasis of the packets.

    """
    _logger.info("Metrics worker starting on thread {}.".format(thread_id))

    while True:
        try:
            p = q.get(block=True, timeout=10)
            _logger.debug("Thread {}: Consumed Packet {}: Queue size is now {}.".format(thread_id, p, q.qsize()))
            sleep(random()+0.7)
        except Empty:
            _logger.info("Thread {}: queue empty.".format(thread_id))
            sleep(1)

if __name__ == "__main__":
    metrics()
