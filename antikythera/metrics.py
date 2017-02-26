#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Analysis of the recieved packets.

"""
import sys
import logging

from queue import Queue, Empty, Full

_logger = logging.getLogger(__name__)


def metrics(thread_id, q):
    """ Perform analyasis of the packets.

    """
    _logger.info("Metrics worker starting on thread {}.".format(thread_id))

    while True:
        try:
            _logger.debug("Thread {}: consuming.".format(thread_id))
            p = q.get(block=True, timeout=10)
            q.task_done()
            sleep(0.01)
        except Empty:
            _logger.info("Thread {}: queue empty.".format(thread_id))
            sleep(0.01)

if __name__ == "__main__":
    anti()
