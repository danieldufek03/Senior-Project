#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Polymorphic Packet Factory

Example:
    Packet making factories can be added using the the ``addFactory()``
    method. These are stored in the ``factories`` dictionary as ``id``
    ``Factory`` pairs.

        >>> from factory import PacketFactory
        >>> factory = PacketFactory
        >>> factory.addFactory("System", System.Factory)
        >>> sys_pkt = factory.createPacket("System", "Type1", '\x42')
        >>> sys_pkt.data()
        'B'

"""

import logging

# Local Imports
from system import System

# from antikythera import __version__

class PacketFactory:
    """ 

    """
    factories = {}
    @staticmethod
    def addFactory(id, packetFactory):
        PacketFactory.factories[id] = packetFactory
    @staticmethod
    def createPacket(id, type, data):
        if PacketFactory.factories[id] not in PacketFactory.factories:
            PacketFactory.factories[id] = eval(id + '.Factory()')
        return PacketFactory.factories[id].create(type, data)
