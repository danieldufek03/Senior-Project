#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" metrics.py

Implementation of the metrics that detect IMSI Catchers

Acronyms:

    ARFCN: Absolute Radio Frequency Channel Number, a unique number
        given to each radio channel in GSM. The ARFCN can be used to
        calculate the exact frequency of the radio channel.
    IMSI: International Subscriber Identity
    LAC: Location Area Code
    CID: Cell Identification Code
    N-CELL-LAC: Neighboring Cell Location Area Code

Reference:

    SnoopSnitch Metrics:
        https://opensource.srlabs.de/projects/snoopsnitch/wiki/IMSI_Catcher_Score

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
    def __init__(self, process_id, sharedMemory=None, *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.shared = sharedMemory
        self.data_dir = appdirs.user_data_dir("anti.sqlite3", "anything")

        _logger.debug("{}: Process started successfully"
                      .format(self.process_id))

        self.exit = mp.Event()

    def run(self):
        """Main process loop.

        """
        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
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

        cursor.execute('''CREATE TABLE IF NOT EXISTS LAC_CID(
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

        cursor.execute('''CREATE TABLE IF NOT EXISTS NEIGHBORS(
                            HASH TEXT PRIMARY KEY,
                            UnixTime REAL,
                            PeopleTime TEXT,
                            CHANNEL TEXT,
                            DBM TEXT,
                            ARFCN TEXT,
                            FrameNumber TEXT,
                            LAC TEXT,
                            CID TEXT,
                            N_CELL_LAC TEXT
                            )''')

        conn.close()
        while not self.exit.is_set():
            _logger.debug("{}: metrics loop begin".format(self.process_id))
            suspectMetrics = [ self.imposter_cell(), self.inconsistent_lac(), self.lonely_cell_id()]
            sleep(3)

            level = 5 - suspectMetrics.count(True)
            _logger.fatal("Metrics: Threat level changed to " + str(level))
            self.shared['defconLevel'].value = level

            #if level != 5:
            #    break
            


        _logger.info("{}: Exiting".format(self.process_id))

    def imposter_cell(self):
        """ Same LAC/CID on different ARFCNs

        A cell is received on different ARFCNs (frequencies) within
        a short time.

        Rationale:

            To avoid leaving traces of a new, non-existent cell, an IMSI
            catcher may choose to reuse the cell ID and LAC of an existing
            cell in an area, but using a different frequency. The IMSI
            catcher must have a location area different from the current
            serving cell, such that the MS performs a location update once
            it close enough. The use of the cell ID on different frequencies
            may be detected by the analysis if system information of the
            original cell was received earlier.

        False Positives:

            A cell may be reconfigured to use a different frequency, but this
            should happen very rarely.

        Example:

            A simple example would be a single two identical CID and LAC pairs
            advertising different ARFCNs.

            * Good Cell
                * LAC 1
                * CID 7
                * ARFCN 42
            * Evil Cell
                * LAC 1
                * CID 7
                * ARFCN 1337

            The evil cell is pretending to be in the location area code to
            not trigger a lonely LAC metric, and to not leave a trace of a
            strange cell wandering all over town.

        Reference:

            SnoopSnitch Metrics:
                https://opensource.srlabs.de/projects/snoopsnitch/wiki/IMSI_Catcher_Score#A4-Same-LACCID-on-different-ARFCNs

        The following SQL query will find packets that share the same
        Location Area Code and Cell ID, but have different ARFCNs.

        """
        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("""SELECT *
                        FROM (
                        SELECT *
                        FROM LAC_CID
                        GROUP BY ARFCN)
                        GROUP BY LAC, CID
                        HAVING COUNT(*) > 1""")

        area_cid_list = []

        for row in cursor.fetchall():
            _logger.debug("{}: {}".format(self.process_id, row))
            area_cid_list.append(row)
        _logger.debug("{}: Length of LAC CID list {}"
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

        The LAC of the current base station differs from the LAC of many
        neighboring cells.

        Rationale:

            A mobile will only perform a normal location update when changing
            to a different area, i.e. a base station with a different LAC. An
            IMSI catcher needs to force a location update to be able to interact
            with the phone and derive the desired information. Therefore, it
            must span a cell with a LAC different to all neighboring cells,
            but with a much better signal strength than the other cells. For
            an IMSI catcher announcing realistic neighboring cells, this
            difference between the LAC of the serving cell and all neighboring
            cell can be detected.

        False Positives:

            Femto cells may or may not announce a LAC different from all
            their neighboring cells. Their may be other special situations,
            like in-house cells where this is the case.

        Example:

            A simple example would be a LAC being the only observed LAC.

            * Evil IMSI Catcher Reports:
                * CID 1337
                * LAC 13
            * All neighboring cells reported by Evil IMSI Catcher are:
                * LAC 7

            The evil cell is pretending to be in the location area code to
            not trigger a lonely LAC metric, and to not leave a trace of a
            strange cell wandering all over town. It is detected by all
            cells it advertises having a different LAC.

            The information must be obtained form the Evil Cells reporting
            of neighboring cells.

        Reference:

            SnoopSnitch Metrics:
                https://opensource.srlabs.de/projects/snoopsnitch/wiki/IMSI_Catcher_Score#A4-Same-LACCID-on-different-ARFCNs



        The following sql query pull the area code that differs by
        datetime minus 5 minutes and places it into a seperate
        table INCONSISTENT_AREA_CODE.

        """
        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
        cursor = conn.cursor()

        inconsistent_lacs = []
        cursor.execute("""SELECT DISTINCT LAC
            FROM NEIGHBORS
            EXCEPT
            SELECT DISTINCT LAC
            FROM NEIGHBORS
            WHERE LAC = CID""")
        for row in cursor.fetchall():
            _logger.debug("{}: {}".format(self.process_id, row))
            inconsistent_lacs.append(row)

        conn.close()

        _logger.debug("{}: Length of inconsistent LAC list {}"
                      .format(self.process_id, len(inconsistent_lacs)))

        if len(inconsistent_lacs):
            _logger.info("{}: Inconsistent LAC Detected."
                         .format(self.process_id))
            return True
        else:
            return False

    def lonely_cell_id(self):
        """Lonesome LAC.

        A cell is the only cell observed in its location area.

        Rationale:

            A mobile will only perform a normal location update when changing
            to a different area, i.e. a base station with a different LAC. An
            IMSI catcher needs to force a location update to be able to interact
            with the phone and derive the desired information. Therefore, it
            must span a cell with a LAC different to all neighboring cells,
            but with a much better signal strength than the other cells. An
            IMSI catcher creating a new LAC for its fake cell will be the
            only cell operating in this location area. The lack of system
            information for other cells of this location area can be detected.

        False Positives:

            When traveling at high speeds or in areas with poor coverage the
            mobile may record system information for only a single cell of
            location area.

            "Unexpected neighbors also do happen often with subway cells. In
            some cases the BTS is in a central place, and the RF heads are far
            away, connected with optical fiber. In these cases cell IDs and
            LACs are carried over many kilometers into places where they
            usually do not belong, and often not all neighbors are set
            correctly, due to restrictions in neighbor list size. I can
            imagine that such circumstances could trigger a false positive."

        Example:

            A simple example would be a group or two of cells sharing a LAC
            and another LAC detected with only a single CID belonging to it.

            * LAC 1 contains CIDs: 1, 2, 3
            * LAC 2 contains CIDs: 4, 5, 6, 6, 8
            * LAC 3 contains CIDs: 9

            Here LAC 3, containing only a single CID is suspicious.

        Reference:

            SnoopSnitch Metrics:
                https://opensource.srlabs.de/projects/snoopsnitch/wiki/IMSI_Catcher_Score#A5-Lonesome-location-area

            SRLabs:
                https://lists.srlabs.de/pipermail/gsmmap/2015-March/001272.html

        """
        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
        cursor = conn.cursor()
        lonely_list = []

        cursor.execute("""SELECT *
            FROM
            (SELECT *
                FROM LAC_CID
                GROUP BY LAC,CID)
            GROUP BY LAC
            HAVING COUNT(LAC) = 1""")

        for row in cursor.fetchall():
            _logger.debug("{}: {}".format(self.process_id, row))
            lonely_list.append(row)

        conn.close()

        _logger.debug("{}: Length of lonely list {}"
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
