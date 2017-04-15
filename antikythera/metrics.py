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
        self.areaCidList = []
        self.inconLACList = []
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

        self.c.execute('''CREATE TABLE IF NOT EXISTS INCON_LAC(
            LAC TEXT,
            PeopleTime TEXT
            )'''
        )

        self.c.execute('''CREATE TABLE IF NOT EXISTS TEST_LAC(
            LAC TEXT,
            PeopleTime TEXT
            )'''
        )

        self.conn.close()
        while not self.exit.is_set():
            _logger.debug("{}: doing metrics stuff".format(self.process_id))
            self.sameAreaAndCellId()
            self.incon_LAC()
            sleep(3)
            self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
            self.c = self.conn.cursor()

            self.c.execute("SELECT * FROM PACKETS")
            for row in self.c.fetchall():   
            	_logger.trace("{}: {}".format(self.process_id, row))
            	self.packetList.append(row)
            self.conn.close()
        
        sizeOfPacketList = len(self.packetList)
        _logger.debug("{}: Length of packetList {}".format(self.process_id, sizeOfPacketList))

        _logger.trace("{}: Packet list content {}".format(self.process_id, self.packetList))
        
        _logger.info("{}: Exiting".format(self.process_id))


    """
    The following sql query will find packets that share the same Location Area Code and Cell ID, but have different frequencies.
    """
    def sameAreaAndCellId(self):
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()

        self.c.execute("""SELECT A.*
            FROM PACKETS A
            INNER JOIN (SELECT LAC, CID, ARFCN
                        FROM PACKETS
                        GROUP BY LAC, CID
                        HAVING COUNT(*) > 1) B
            ON A.LAC = B.LAC AND A.CID = B.CID AND A.ARFCN <> B.ARFCN""")
        for row in self.c.fetchall():
            _logger.trace("{}: {}".format(self.process_id, row))
            self.areaCidList.append(row)
        sizeOfAreaCidList = len(self.areaCidList)
        _logger.trace("{}: Length of areaCidList {}".format(self.process_id, sizeOfAreaCidList))
        self.conn.close()

    """
    The following sql query pull LAC that differ by PeopleTime.
    """
    def incon_LAC(self):
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()

        self.c.execute("INSERT INTO INCON_LAC SELECT LAC, PeopleTime FROM PACKETS")
        self.c.execute(
            """INSERT INTO TEST_LAC(
            LAC,
            PeopleTime
            ) VALUES (?, ?)
            """, (
                '757',
                '2015-07-2007:30:00'
                )
            )
            #self.c.execute("SELECT * FROM INCON_LAC")
            #self.c.execute("SELECT * FROM TEST_LAC")
        self.c.execute("""SELECT LAC FROM INCON_LAC
             WHERE PeopleTime != 
            (SELECT PeopleTime FROM TEST_LAC)""")
        for row in self.c.fetchall():
            _logger.trace("{}: {}".format(self.process_id, row))
            self.inconLACList.append(row)
        sizeOfinconLACList = len(self.inconLACList)
        _logger.trace("{}: Length of inconLACList {}".format(self.process_id, sizeOfinconLACList))
        self.conn.close()

    def shutdown(self):

        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()


if __name__ == "__main__":
    decoder()
