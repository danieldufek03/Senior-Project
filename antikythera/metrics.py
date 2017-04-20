#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Implementation of the metrics that detect IMSI Catchers

"""
import logging
import sqlite3
import datetime
import multiprocessing as mp
from multiprocessing import Process
from time import sleep

import appdirs

_logger = logging.getLogger(__name__)
__author__ = "TeamAwesome"


class Metrics(Process):
    """The metrics

    """
    def __init__(self, process_id, *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.datadir = appdirs.user_data_dir("anti.sqlite3", "anything")
        _logger.debug("{}: Process started successfully"
                      .format(self.process_id))
        self.exit = mp.Event()

    def run(self):
        """Main process loop.

        """
        conn = sqlite3.connect(self.datadir, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS PACKETS(
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

        cursor.execute('''CREATE TABLE IF NOT EXISTS INCONSISTENT_AREA_CODE(
                        LAC TEXT,
                        PeopleTime TEXT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS TEMP_PREVIOUS_TIME(
                        LAC TEXT,
                        PreviousTime TEXT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS PAGE(
                            HASH TEXT PRIMARY KEY,
                            UnixTime REAL,
                            PeopleTime TEXT,
                            CHANNEL TEXT,
                            DBM TEXT,
                            ARFCN TEXT,
                            FrameNumber TEXT,
                            idType TEXT,
                            msgType TEXT,
                            MODE TEXT,
                            reqChanOne TEXT,
                            reqChanTwo TEXT
                            )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS SYSTEM(
                            HASH TEXT PRIMARY KEY,
                            UnixTime REAL,
                            PeopleTime TEXT,
                            CHANNEL TEXT,
                            DBM TEXT,
                            ARFCN TEXT,
                            FrameNumber TEXT,
                            LAC TEXT,
                            CID TEXT
                            )''')

        conn.close()
        while not self.exit.is_set():
            _logger.trace("{}: metrics loop begin".format(self.process_id))
            self.imposter_cell()
            self.inconsistent_lac()
            self.lonely_cell_id()
            sleep(3)
            conn = sqlite3.connect(self.datadir, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PACKETS")

            packet_list = []
            for row in cursor.fetchall():
                _logger.trace("{}: {}".format(self.process_id, row))
                packet_list.append(row)
            conn.close()

        _logger.trace("{}: Length of packet list {}"
                      .format(self.process_id, len(packet_list)))

        _logger.trace("{}: Packet list content {}"
                      .format(self.process_id, packet_list))

        _logger.info("{}: Exiting".format(self.process_id))

    def imposter_cell(self):
        """ Same LAC/CID on different ARFCNs

        The following SQL query will find packets that share the same
        Location Area Code and Cell ID, but have different frequencies.

        """
        conn = sqlite3.connect(self.datadir, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("""SELECT *
                        FROM (
                        SELECT *
                        FROM SYSTEM
                        GROUP BY ARFCN)
                        GROUP BY LAC, CID
                        HAVING COUNT(*) > 1""")

        area_cid_list = []
        for row in cursor.fetchall():
            _logger.trace("{}: {}".format(self.process_id, row))
            area_cid_list.append(row)
        _logger.trace("{}: Length of LAC CID list {}"
                      .format(self.process_id, len(area_cid_list)))

        conn.close()

        if len(area_cid_list):
            _logger.info("{}: Same LAC/CID on different ARFCNs detected."
                         .format(self.process_id))
            return True
        else:
            return False

    def inconsistent_lac(self):
        """ Inconsistent LAC

        The following sql query pull the area code that differs by
        datetime minus 5 minutes and places it into a seperate
        table INCONSISTENT_AREA_CODE.

        """
        conn = sqlite3.connect(self.datadir, check_same_thread=False)
        cursor = conn.cursor()

        self.create_temp_table_previous_time()

        cursor.execute("""INSERT INTO INCONSISTENT_AREA_CODE SELECT LAC,
                        PeopleTime FROM PACKETS""")

        cursor.execute("""SELECT LAC, PeopleTime FROM INCONSISTENT_AREA_CODE
                        WHERE PeopleTime >
                        (SELECT PreviousTime FROM TEMP_PREVIOUS_TIME)""")

        inconsistent_lacs = []
        for row in cursor.fetchall():
            _logger.trace("{}: {}".format(self.process_id, row))
            inconsistent_lacs.append(row)

        conn.close()

        _logger.trace("{}: Length of inconsistent LAC list {}"
                      .format(self.process_id, len(inconsistent_lacs)))

        if len(inconsistent_lacs):
            _logger.info("{}: Inconsistent LAC Detected."
                         .format(self.process_id))
            return True
        else:
            return False

    def create_temp_table_previous_time(self):
        """ Create temp table.

        Create a temp table that houses local area code and a preivious
        time stamp for verification purposes.

        """
        prev_time = (datetime.datetime.now() -
                     datetime.timedelta(days=730, minutes=5))

        conn = sqlite3.connect(self.datadir, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO TEMP_PREVIOUS_TIME(
            LAC,
            PreviousTime
            ) VALUES (?, ?)
            """, (
                ("SELECT LAC FROM PACKETS"),
                prev_time
                )
            )

        previous_time_list = []
        for row in cursor.fetchall():
            _logger.trace("{}: {}".format(self.process_id, row))
            previous_time_list.append(row)
        _logger.trace("{}: Length of previous time list {}"
                      .format(self.process_id, previous_time_list))

    def lonely_cell_id(self):
        """ Lonesome location area.

        The location area code should have multiples of the same cell-ID
        assigned to it. There should not be single unique instance of a
        cell-ID within a location area. If there are any packets that
        fall into that criteria, they will be caught with the following
        function.

        """
        conn = sqlite3.connect(self.datadir, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT LAC FROM SYSTEM")

        query_list = []
        for lac in cursor.fetchall():
            query_list.append(lac)

        lonely_list = []
        for lac in query_list:
            cursor.execute("""SELECT *
                FROM (
                    SELECT LAC, CID
                    FROM SYSTEM
                    WHERE SYSTEM.LAC = ?
                    )
                GROUP BY CID
                HAVING COUNT(CID) = 1""", lac)

            for row in cursor.fetchall():
                _logger.trace("{}: {}".format(self.process_id, row))
                lonely_list.append(row)

        conn.close()

        _logger.trace("{}: Length of lonely list {}"
                      .format(self.process_id, len(lonely_list)))

        if len(lonely_list):
            _logger.info("{}: Lonesome Location Area Code Detected."
                         .format(self.process_id))
            return True
        else:
            return False

    def shutdown(self):
        """ Trigger shutdown and exit of ``run()`` when called by manager.

        """
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()


if __name__ == "__main__":
    pass
