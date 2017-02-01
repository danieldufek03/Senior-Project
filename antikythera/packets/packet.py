#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 

"""

# Standard Library
import logging

from time import time
from datetime import datetime

# Local


__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

class Packet(object):
    def __init__(self):
        self.unix_time = time()
        self.timestamp = datetime.utcnow()
        self.location = "location stub"
