#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import sys
import logging

__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

class  Assign(Packet):
    def __init__(self):
        self.packet_class = "Immediate Assignment"

    class Factory:
        @staticmethod
        def create(type):
            if type == "Type1": return Type1(data)
            else:
                _logger.critical("Bad packet creation of type: " + type)
                sys.exit(127)
