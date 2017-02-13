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
    """ Type1 GSM System Information Packet.

    Args:
        data: the data to construct the packet with.

    Attributes:
        self_arfcns: Absolute Radio Frequency Channel Numbers of the
            broadcasting cell.

    """
    def __init__(self, data):
        super().__init__()
        self.data = self.decode(data)
    def __str__(self):
        return "Type1 system information packet"
    def decode(self, data):
        return data

class Type2(System):
    """ Type2 GSM System Information Packet.

    Args:
        data: the data to construct the packet with.

    Attributes:
        neighbor_arfcns: Absolute Radio Frequency Channel Numbers of
            neighboring cells.

    """
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        return "Type2 system information packet"
    def decode():
        return data

class Type3(System):
    """ Type3 GSM System Information Packet.

    Args:
        data: the data to construct the packet with.

    Attributes:
        cell_id: The broadcasting base stations Cell ID (CID).
        lai: Location Area Identity (LAI) this consists of the Mobile.
            Country Code (MCC) the Mobile Network Code (MNC) and the
            Location Area Code (LAC). They are concatenated together
            in that order.
        gprs: General Radio Packet Service (GRPS) information.

    """
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        return "Type3 system information packet"
    def decode():
        return data

class Type4(System):
    """ Type4 GSM System Information Packet.

    Args:
        data: the data to construct the packet with.

    Attributes:
        lai: Location Area Identity (LAI) this consists of the Mobile.
            Country Code (MCC) the Mobile Network Code (MNC) and the
            Location Area Code (LAC). They are concatenated together
            in that order.
        select_params: Cell selection parameters.
        gprs: General Radio Packet Service (GRPS) information.

    """
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        return "Type4 system information packet"
    def decode():
        return data

class Type2ter(System):
     """ Type4 GSM System Information Packet.

    Args:
        data: the data to construct the packet with.

    Attributes:
        neighbor_disc: Verbose neighboring cell description.
        neighbor_arfcns: Absolute Radio Frequency Channel Numbers of
            neighboring cells.

    """
    def __init__(self, data):
        super().__init__()
        self.data = decode()
    def __str__(self):
        return "Type2ter system information packet"
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
