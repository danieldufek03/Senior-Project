#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Implementation of the metrics that detect IMSI Catchers

"""
import logging
import sqlite3
import appdirs
import multiprocessing as mp

from time import sleep
from multiprocessing import Process, Queue

_logger = logging.getLogger(__name__)
__author__ = "TeamAwesome"

class Metrics(Process):
    """ The metrics

    """

    def __init__(self, process_id, *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.datadir = appdirs.user_data_dir("anti.sqlite3", "anything")
        self.conn = None
        self.c = None
        self.packetList = []
        _logger.debug("{}: Process started successfully".format(self.process_id))
        self.exit = mp.Event()

    def run(self):
        """

        """
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS PACKETS(
        	UnixTime REAL,
            PeopleTime TEXT,
            CHANNEL TEXT,
            DBM TEXT,
            ARFCN TEXT,
            TMSI TEXT,
            IMSI TEXT,
            LAC TEXT,
            CID TEXT,
            MCC TEXT,
            MNC TEXT,
            IMEISV TEXT,
            FrameNumber TEXT,
            HASH TEXT PRIMARY KEY
            )'''
    	)
        self.conn.close()
        while not self.exit.is_set():
            _logger.debug("{}: doing metrics stuff".format(self.process_id))
            sleep(3)
            self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
            self.c = self.conn.cursor()

            self.c.execute("SELECT * FROM PACKETS")
            for row in self.c.fetchall():   
            	_logger.trace("{}: {}".format(self.process_id, row))
            	self.packetList.append(row)
            self.conn.close()
        
        sizeOfPacketList = len(self.packetList)
        _logger.trace("{}: Length of packetList {}".format(self.process_id, sizeOfPacketList))
        set(self.packetList)
        newSizeOfPacketList = len(self.packetList)
        _logger.trace("{}: Length of 'set' packetList {}".format(self.process_id, newSizeOfPacketList))
        
        print(self.packetList)
        _logger.info("{}: Exiting".format(self.process_id))


    def shutdown(self):
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()


if __name__ == "__main__":
    decoder()
