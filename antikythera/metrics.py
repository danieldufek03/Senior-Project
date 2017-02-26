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
    _logger.info("Metrics worker process {} starting.".format(process_id))

    while True:
        try:
            p = q.get(block=True, timeout=10)
            _logger.debug("Process {} consumed packet {}: Queue size is now {}.".format(process_id, p, q.qsize()))
            sleep(random()+2)
        except Empty:
            _logger.warning("Process {} Queue empty.".format(process_id))
            sleep(1)

if __name__ == "__main__":
    metrics()
