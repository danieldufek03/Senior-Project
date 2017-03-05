#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Implementation of the metrics that detect IMSI Catchers

"""
import logging

from time import sleep

_logger = logging.getLogger(__name__)

class Metrics():
    """ The metrics

    """

    def __init__(self, process_id):
        """

        """
        self.process_id = process_id
        _logger.debug("{}: Process started successfully".format(self.process_id))

    def metrics(self):
        while True:
            _logger.trace("{}: doing metrics stuff".format(self.process_id))
            sleep(3)


if __name__ == "__main__":
    decoder()
