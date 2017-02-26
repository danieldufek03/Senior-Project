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


def radio(process_id, q):
    """ Grab the packets from the radio interface.

    """
    _logger.info("Radio worker process {} started.".format(process_id))

    i=0
    while True:
        try:
            p = "Packet {}".format(i)
            i+=1
            q.put(p, block=True, timeout=10)
            _logger.debug("Process {} produced packet {}: Queue size is now {}.".format(process_id, p, q.qsize()))
            sleep(random())
        except Full:
            _logger.warning("Process {} cannot write to full Queue.".format(process_id))
            sleep(1)


if __name__ == "__main__":
    radio()
