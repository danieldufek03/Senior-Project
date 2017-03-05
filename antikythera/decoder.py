#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" decoder.py

Unwrap the pyshark packets and put the needed data into the database.

"""
import logging

from random import random
from time import sleep
from queue import Queue, Empty

_logger = logging.getLogger(__name__)


class Decoder():
    """ Decode and store the packets for analysis.

    """

    def __init__(self, process_id, q):
        self.process_id = process_id
        self.q = q


    def decode(self):
        """

        """
        _logger.debug("{}: Process started successfully".format(self.process_id))
        while True:
            try:
                packet = self.q.get(timeout=10)
                _logger.trace("{}: Consumed packet Queue size is now {}".format(self.process_id, self.q.qsize()))
                self.decode_packet(packet)
                self.store_packet(packet)
                sleep(1)
            except Empty:
                _logger.info("{}: Queue empty".format(self.process_id))
                sleep(1)


    def decode_packet(self, packet):
        """ Get only the needed attributes from the packet.

        """
        _logger.trace("{}: Decoding packet {}".format(self.process_id, packet['gsmtap'].frame_nr))
        pass


    def store_packet(self, packet):
        """ Put packet into database.

        """
        _logger.trace("{}: Storing packet {}".format(self.process_id, packet['gsmtap'].frame_nr))
        pass


if __name__ == "__main__":
    decoder()
