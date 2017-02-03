#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GSM system information packets.

"""

import sys
import logging

__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

from packet import Packet

class System(Packet):
    """ System information packet attributes and factory.

    """
    def __init__(self):
        super().__init__()

    class Factory:
        """ System information packet factory.

        """
        @staticmethod
        def create(type, data):
            """ Create a system packet of the given type.

            Args:
                type (str): the type of packet subclass to create.
                data: the data to construct the packet with.

            """
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
        "Type2 system information packet"
    def decode():
        return data

class Type3(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type3 system information packet"
    def decode():
        return data

class Type4(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        return "Type4 system information packet"
    def decode():
        return data

class Type2ter(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type2ter system information packet"
    def decode():
        return data

class Type2quater(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type2quater system information packet"
    def decode():
        return data

class Type13(System):
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        "Type13 system information packet"
    def decode():
        return data
