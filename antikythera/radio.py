#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" radio.py

Interface to the radio and Pcap files.

"""
import sys
import logging

from time import sleep
from queue import Queue, Empty, Full

_logger = logging.getLogger(__name__)


def radio(thread_id, q):
    """ Grab the packets from the radio interface.

    """
    _logger.info("Radio worker starting on thread {}.".format(thread_id))

    i=0
    while True:
        try:
            _logger.debug("Thread {}: producing.".format(thread_id))
            p = "Packet {}".format(i)
            i+=1
            q.put(p, block=True, timeout=10)
            sleep(0.01)
        except Full:
            _logger.info("Thread {}: Queue full.".format(thread_id))
            sleep(0.01)


if __name__ == "__main__":
    anti()
