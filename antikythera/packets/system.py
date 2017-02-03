#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import sys
import logging

__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

from packet import Packet

class System(Packet):
    def __init__(self):
        super().__init__()
        self.packet_class = "System Information"

    class Factory:
        @staticmethod
        def create(type, data):
            if type == "Type1": return Type1(data)
            elif type == "Type2": return Type2(data)
            elif type == "Type3": return Type3(data)
            elif type == "Type4": return Type4(data)
            elif type == "Type2ter": return Type2ter(data)
            elif type == "Type2quater": return Type2quater(data)
            elif type == "Type13": return Type13(data)
            else:
                _logger.critical("Bad packet creation of type: " + type)
                sys.exit(127)

class Type1(System):
    def __init__(self, data):
        super().__init__()
        self.data = self.decode(data)
    def __str__(self):
        "Type1 system information packet"
    def decode(self, data):
        return data

class Type2(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type1 system information packet"
    def decode():
        return data

class Type3(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type1 system information packet"
    def decode():
        return data

class Type4(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        return "Type1 system information packet"
    def decode():
        return data

class Type2ter(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type1 system information packet"
    def decode():
        return data

class Type2quater(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type1 system information packet"
    def decode():
        return data

class Type13(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type1 system information packet"
    def decode():
        return data
