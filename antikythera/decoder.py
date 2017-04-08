#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" decoder.py

Unwrap the pyshark packets and put the needed data into the database.

"""
import logging
import sqlite3
import datetime
import appdirs
import time
import multiprocessing as mp

from random import random
from queue import Empty
from multiprocessing import Process, Queue

_logger = logging.getLogger(__name__)

__author__ = "TeamAwesome"

try:
    import sqlitedict
except ImportError as e:
    _logger.error("Decoder: {}".format(e))
    _logger.info("Decoder: Maybe try `pip install -r requirements.txt'")
    sys.exit(1)


class Decoder(Process):
    """ Decode and store the packets for analysis.

    """

    def __init__(self, process_id, q, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.q = q
        self.exit = mp.Event()

        self.datadir = appdirs.user_data_dir(__name__, __author__)
        self.conn = None
        self.c = None


    def run(self):
        """

        """
        _logger.debug("{}: Process started successfully".format(self.process_id))
        _logger.info("{}: Database storage set to {}".format(self.process_id,
            self.datadir))
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS PACKETS(
            UnixTime REAL,
            PeopleTime TEXT,
            TMSI TEXT,
            IMSI TEXT,
            LAC TEXT,
            CID TEXT,
            ARFCN TEXT,
            MCC TEXT,
            MNC TEXT,
            IMEISV TEXT,
            FrameNumber TEXT,
            HASH TEXT PRIMARY KEY
            )'''
        )
        self.conn.close()
        while not self.exit.is_set():
            try:
                packet = self.q.get(timeout=10)
                _logger.debug("{}: Consumed packet Queue size is now {}".format(self.process_id, self.q.qsize()))
                packet_data = self.decode_packet(packet)
                self.store_packet(packet_data, packet)
            except Empty:
                _logger.info("{}: Queue empty".format(self.process_id))
        _logger.info("{}: Exiting".format(self.process_id))


    def decode_packet(self, packet):
        """ Get only the needed attributes from the packet.

        """
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()
        _logger.debug("{}: Decoding packet {}".format(self.process_id,
            packet['gsmtap'].frame_nr))
        packet_data = {}
        # Prevent collisions when running multiple times on same capture file
        packet_data.update({"hash" : hash((packet.__hash__(), time.time()))})
        packet_data.update({"frame_nr" : float(packet['gsmtap'].frame_nr)})
        packet_data.update({"timestamp" : float(packet.sniff_timestamp)})
        packet_data.update({"datetime" :
            str(datetime.datetime.fromtimestamp(
                    packet_data['timestamp']).strftime('%Y-%m-%d%H:%M:%S')
                )})
        return packet_data


    def store_packet(self, packet_data, packet):
        """ Put packet into database.

        """
        _logger.debug("{}: Storing packet {}".format(self.process_id,
            packet['gsmtap'].frame_nr))
        self.c.execute(
            """INSERT INTO PACKETS(
                UnixTime,
                PeopleTime,
                TMSI,
                IMSI,
                LAC,
                CID,
                ARFCN,
                MCC,
                MNC,
                IMEISV,
                FrameNumber,
                HASH
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                packet_data['timestamp'],
                packet_data['datetime'],
                '123456789012345',
                '324345566767899',
                '303',
                '151515',
                '131313',
                '232',
                '02',
                '1234567891234567',
                packet_data['frame_nr'],
                packet_data['hash']
            )
        )
        self.conn.commit()
        self.conn.close()


    def shutdown(self):
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()


if __name__ == "__main__":
    Decoder()
