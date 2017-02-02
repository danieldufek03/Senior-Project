#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Polymorphic Packet Factory

``PacketFactory`` allows different types of packet factories to be
subclassed from the base class. This is desirable to make the
definition of packets used flexible for both quickly evolving
technologies and security counter and counter-counter measures.

Example:
    Packet making factories can be added using the the ``addFactory()``
    method. These are stored in the ``factories`` dictionary as ``id``
    ``Factory`` pairs. Then packets themselves can be created from the
    factory by calling ``createPacket()``with the parameters needed
    to build the packet for the given packet type.

        >>> from factory import PacketFactory
        >>> factory = PacketFactory
        >>> from system import System
        >>> factory.addFactory("System", System.Factory)
        >>> sys_pkt = factory.createPacket("System", "Type1", '\x42')
        >>> sys_pkt.data
        'B'

    Note:
        The ``Factory`` objects that will be added must each be imported.

"""

import logging

# Local Imports
from system import System

# from antikythera import __version__

class PacketFactory:
    """ A Polymorphic Packet Factory

    A factory for creating and using packet factories.

    Attributes:
        factories (dict): a dictionary containing some identifier value as keys
            and ``Factory`` objects stored as the pair. 

    """
    factories = {}


    @staticmethod
    def addFactory(id, factory):
        """ Add an {identifier : ``Factory``} object pair to ``factories``.

        Args:
            param1 id: the identifier can be any valid key type for a python
                dictionary.
            param2 (:obj:`factory`): a packet factory subclass.

        """
        PacketFactory.factories[id] = factory


    @staticmethod
    def createPacket(id, type, data):
         """ Add an {identifier : ``Factory``} object pair to ``factories``.

        Args:
            param1 id: A dictionary key corresponding to a key in the
                ``factories`` dictionary. This selects the subclassed
                factory to create the packet from.
            param2 type: the selector for the type of packet the
                subclassed factory should create.
            param3 data: the data to construct the packet from.

        Returns:
            :obj:`Packet`: A packet object from the specified sub-sub-class,
                constructed with the given data.

        """
       if PacketFactory.factories[id] not in PacketFactory.factories:
            PacketFactory.factories[id] = eval(id + '.Factory()')
        return PacketFactory.factories[id].create(type, data)
