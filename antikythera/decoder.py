#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" decoder.py

Unwrap the pyshark packets and put the needed data into the database.

"""
import sys
import time
import logging
import sqlite3
import datetime
import random
import multiprocessing as mp
from multiprocessing import Process
from queue import Empty

_logger = logging.getLogger(__name__)

__author__ = "TeamAwesome"

try:
    import appdirs
except ImportError as error:
    _logger.error("Decoder: {}".format(error))
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

        self.datadir = appdirs.user_data_dir("anti.sqlite3", "anything")
        self.conn = None
        self.c = None

    def run(self):
        """ Process main function, program loop.

        """
        _logger.debug("{}: Process started successfully".format(
            self.process_id))
        _logger.info("{}: Database storage set to {}".format(self.process_id,
                                                             self.datadir))
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
                            )''')
        self.conn.close()
        while not self.exit.is_set():
            try:
                packet = self.q.get(timeout=10)
                _logger.debug("{}: Consumed packet Queue size is now {}".format(
                    self.process_id, self.q.qsize()))
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
        _logger.debug("{}: Decoding packet {}".format(
            self.process_id, packet['gsmtap'].frame_nr))

        packet_data = {}

        # Prevent collisions when running multiple times on same capture file
        packet_data.update({"hash": hash((packet.__hash__(), time.time()))})

        # Layer common to all packets
        packet_data.update({"frame_nr": float(packet['gsmtap'].frame_nr)})
        packet_data.update({"channel": float(packet['gsmtap'].chan_type)})
        packet_data.update({"signal_dbm": float(packet['gsmtap'].signal_dbm)})
        packet_data.update({"arfcn": float(packet['gsmtap'].arfcn)})
        packet_data.update({"timestamp": float(packet.sniff_timestamp)})
        packet_data.update({"datetime":
                            str(datetime.datetime.fromtimestamp(
                                packet_data['timestamp']).strftime(
                                    '%Y-%m-%d%H:%M:%S'))})

        # Detect packet type and extract needed data
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
                CHANNEL,
                DBM,
                ARFCN,
                TMSI,
                IMSI,
                LAC,
                CID,
                MCC,
                MNC,
                IMEISV,
                FrameNumber,
                HASH
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                packet_data['timestamp'],
                packet_data['datetime'],
                packet_data['channel'],
                packet_data['signal_dbm'],
                packet_data['arfcn'],
                '123456789012345',
                '324345566767899',
                random.randint(1,200),
                random.randint(1,200),
                '131313',
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
    Decoder(0, 0)
