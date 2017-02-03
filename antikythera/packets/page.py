#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GSM paging packets.

"""

import sys
import logging

from packet import Packet

__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

class  Page(Packet):
    """ Paging packet attributes and factory.

    """
    def __init__(self):
        super().__init__()
        self.packet_class = "Paging"

    class Factory:
        """ Paging packet factory.

        """
        @staticmethod
        def create(type):
            """ Create a paging packet of the given type.

            Args:
                type (str): the type of packet subclass to create.
                data: the data to construct the packet with.

            """
            if type == "Type1": return Type1(data)
            elif type == "Type2": return Type2(data)
            elif type == "Type3": return Type3(data)
            else:
                _logger.critical("Bad packet creation of type: " + type)
                sys.exit(127)

