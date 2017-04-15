#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Implementation of the metrics that detect IMSI Catchers

"""
import logging
import sqlite3
import appdirs
import datetime
import multiprocessing as mp

from time import sleep
from datetime import timedelta
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
        self.inconsistentAreaCodeList = []
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

        self.c.execute('''CREATE TABLE IF NOT EXISTS INCONSISTENT_AREA_CODE(
            LAC TEXT,
            PeopleTime TEXT
            )'''
        )

        self.c.execute('''CREATE TABLE IF NOT EXISTS TEMP_INCONSISTENT_AREA_CODE(
            LAC TEXT,
            PreviousTime TEXT
            )'''
        )

        self.conn.close()
        while not self.exit.is_set():
            _logger.debug("{}: doing metrics stuff".format(self.process_id))
            self.sameAreaAndCellId()
            self.inconsistentAreaCode()
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
        #PrevTime = datetime.datetime.now() - datetime.timedelta(days = 730, minutes=5)

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
    The following sql query pull the area code that differs by datetime minus 5 minutes
    and places it into a seperate table INCONSISTENT_AREA_CODE.
    """
    def inconsistentAreaCode(self):
        PrevTime = datetime.datetime.now() - datetime.timedelta(days = 730, minutes=5)
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()

        self.c.execute("INSERT INTO INCONSISTENT_AREA_CODE SELECT LAC, PeopleTime FROM PACKETS")
        self.c.execute(
            """INSERT INTO TEMP_INCONSISTENT_AREA_CODE(
            LAC,
            PreviousTime
            ) VALUES (?, ?)
            """, (
                '757',
                PrevTime
                )
            )
        #self.c.execute("SELECT * FROM INCON_LAC")
        #self.c.execute("SELECT * FROM TEMP_INCONSISTENT_AREA_CODE")
        self.c.execute("""SELECT LAC, PeopleTime FROM INCONSISTENT_AREA_CODE
             WHERE PeopleTime > 
            (SELECT PreviousTime FROM TEMP_INCONSISTENT_AREA_CODE)""")
        for row in self.c.fetchall():
            _logger.debug("{}: {}".format(self.process_id, row))
            self.inconsistentAreaCodeList.append(row)
        sizeOfinconsistentAreaCodeList = len(self.inconsistentAreaCodeList)
        _logger.trace("{}: Length of inconsistentAreaCodeList {}".format(self.process_id, sizeOfinconsistentAreaCodeList))
        self.conn.close()

    def shutdown(self):

        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()


if __name__ == "__main__":
    decoder()
