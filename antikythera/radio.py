#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" radio.py

Interface to the radio and Pcap files.

"""
import logging

from random import random
from time import sleep
from queue import Queue, Full

_logger = logging.getLogger(__name__)


def radio(thread_id, q):
    """ Grab the packets from the radio interface.

    """
    _logger.info("Radio worker starting on thread {}.".format(thread_id))

    i=0
    while True:
        try:
            p = "Packet {}".format(i)
            i+=1
            q.put(p, block=True, timeout=10)
            _logger.debug("Thread {}: Produced Packet {}: Queue size is now {}.".format(thread_id, p, q.qsize()))
            sleep(random())
        except Full:
            _logger.debug("Thread {}: Queue full.".format(thread_id))
            sleep(1)


if __name__ == "__main__":
    radio()
