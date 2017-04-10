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
        self.datadir = appdirs.user_data_dir(__name__, __author__)
        self.conn = None
        self.c = None
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
            _logger.debug("{}: Number of Rows... {}".format(self.process_id, len(self.c.fetchall())))
            _logger.debug("{}: Data...{}".format(self.process_id, self.c.fetchall()))
            for row in self.c.fetchall():   
            	_logger.debug("{}: {}".format(self.process_id, row))
            self.conn.close()
        _logger.info("{}: Exiting".format(self.process_id))


    def shutdown(self):
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()


if __name__ == "__main__":
    decoder()
