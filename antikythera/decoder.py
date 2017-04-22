#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" decoder.py

Unwrap the pyshark packets and put the needed data into the database.

Abbreviations:

    RXLEV: Reception Level (GSM).

    NCELL: neighboring cell.

    BSIC-NCELL: Abbreviation for Base Station Identity Code of
        an adjacent CELL. Identifies and decode the BCCH (Broadcast
        Control Channel) of neighbouring cells so that the MS
        (Mobile Station) may take measuring reports to facilitate
        handover, or to allow the MS to make cell selection and
        reselection calculations.

    NO-NCELL-M: No neighbour cell measurement result. One byte
        unsigned integer representing the number of neighbour
        cells.

    FULL vs. SUB Values:
        In GSM, there are two types of values presented for RxQual,
        namely RxQual Full and RxQual Sub. RxLev, the parameter
        representing the signal strength, also has similar Full
        and Sub values. The FULL values are based upon all frames
        on the SACCH multiframe, whether they have been transmitted
        from the base station or not. This means that if DTX DL has
        been used, the FULL values will be invalid for that period
        since they include bit-error measurements at periods when
        nothing has been sent resulting in very high BER. In total,
        100 bursts (25 blocks) will be used for the FULL values.

        The SUB values are based on the mandatory frames on the SACCH
        multiframe. These frames must always be transmitted. There
        are two frames fulfilling that criteria and that is the
        SACCH block (A bursts in Figure 7) and the block holding
        the SID frame. If DTX DL is not in use, the SID frame will
        contain an ordinary speech frame and then this is included
        instead. In total, 12 bursts (two blocks) will be used for
        the SUB values (four bursts SACCH and eight half bursts
        [or speech] information).

Further Reference:

    https://www.google.com/patents/US8619608
    http://www.sharetechnote.com/html/BasicCallPacket_GSM.html#Step_15

"""
import sys
import time
import logging
import sqlite3
import datetime
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
    """Decode and store the packets for analysis.

    The ``run()`` function is the process main loop. It first sets up
    the tables needed by the ``PacketManager`` to sort the packets
    into with ``create_tables()``. Then until the Multiprocessing
    event ``exit`` is set by the manager process it continually
    pulls packets out of the shared ``queue`` and hands them off
    to the ``PacketManager`` for processing.

    """
    def __init__(self, process_id, queue, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.queue = queue
        self.exit = mp.Event()
        self.data_dir = appdirs.user_data_dir("anti.sqlite3", "anything")

    def run(self):
        """Process main function, program loop.

        Perform initial setup by creating tables and the
        ``PacketManager``, then execute the run loop to pass
        packets from the ``queue`` to be inserted into the
        database until ``shutdown()`` is called.

        """
        _logger.debug("{}: Process started successfully".format(
            self.process_id))
        _logger.info("{}: Database storage set to {}".format(self.process_id,
                                                             self.data_dir))
        self.create_tables()
        packet_manager = PacketManager(self.process_id, self.data_dir)
        while not self.exit.is_set():

            try:

                packet = self.queue.get(timeout=10)
                _logger.trace("{}: Consumed packet Queue size is now {}".format(
                    self.process_id, self.queue.qsize()))
                packet_manager.insert_packet(packet)

            except Empty:
                _logger.info("{}: Queue empty".format(self.process_id))
        _logger.info("{}: Exiting".format(self.process_id))

    def shutdown(self):
        """When manager process requests exit run loop and terminate.

        """
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()

    def create_tables(self):
        """Create packet tables.

        Create all tables required by the ``PacketManager`` if they
        do not exist. Data that is in the GSMTAP layer of the packets
        is common between all packets and is therefore present in all
        tables. It includes:

        * HASH
        * UnixTime
        * PeopleTime
        * CHANNEL
        * DBM
        * ARFCN
        * FrameNumber

        Everything else is information that is specific to the Packet(s)
        that are inserted in the given table. Tables are created for
        each group of packets data important to a given query.

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

        conn.close()


class PacketManager():
    """Manage operations on packets.

    Attributes:
        process_id (str): Process identifier.
        data_dir (str): Where the database is stored.
        packet_types (dict): Implemented packet types. Keys are packet major
            types and value is a list of implemented subtypes.
        packet_metrics (dict): Returns the table the packet should be sorted
            into given (MAJOR_TYPE + _ + MINOR_TYPE) for example,
            "GSM_A.DTAP_30" representing the system message subtype 30
            which contains LAC and CID information.

    """
    def __init__(self, process_id, data_dir):
        self.process_id = process_id
        self.data_dir = data_dir
        self.packet_factory = PacketFactory()

        self.packet_types = {
            'GSM_A.CCCH': ['33'],
            'GSM_A.DTAP': ['30']
        }

        self.packet_metrics = {
            'GSM_A.CCCH_33': "PAGE",
            'GSM_A.DTAP_30': "LAC_CID"
        }

    def insert_packet(self, packet):
        """Insert only needed data into the database for analysis.

        """
        self.packet = packet
        packet_type, packet_subtype = self.get_packet_type()
        self.store(packet, packet_type, packet_subtype)

    def is_implemented(self, type_, subtype):
        """Return true if packet type/subtype is implemented.

        """
        if type_ in self.packet_types:
            if subtype in self.packet_types[type_]:
                return True
        return False

    def get_packet_type(self):
        """Get the packet type and subtype information.

        Attributes:
            _type (str): The name of the unique packet data layer.
            data_layer: The actual packet data layer object.
            attributes (list): A list of strings with the names of all valid
                attributes and methods for the data layer object.
            index (int): The zero indexed location of the packet. For a live
                capture it would represent the number of packets received.
                For a ``.pcap`` file it is the index that the packet is found
                at if the file is read into a Pyshark object using
                ``FileCapture``.
            no_type (str): An error message used when the packet type is not
                implemented.
            no_subtype (str): An error message used when the packet type is
                implemented but not the subtype.


        Returns: packet type string and subtype int tuple.

        """
        # Get packet properties for sorting
        _type = self.packet.highest_layer
        data_layer = self.packet[self.packet.highest_layer.lower()]
        attributes = self.packet[self.packet.highest_layer.lower()].field_names

        if _type in self.packet_types.keys():
            if 'gsm_a_dtap_msg_rr_type' in attributes:
                _subtype = data_layer.gsm_a_dtap_msg_rr_type
                return (_type, _subtype)
            if 'msg_rr_type' in attributes:
                _subtype = data_layer.msg_rr_type
                return (_type, _subtype)
            return (_type, None)

        return (_type, None)

    def get_packet_info(self, data_layer, _type, _subtype, implemented):
        """Attempt to get a brief description of the packet.

        Arguments:
            data_layer: the highest layer of a GSMTAP format packet.
            _type (str): If a type is found a string representation, else None.
            _subtype (str): If a subtype is found a string representation,
                else None.

        Returns:
            packet_info (str): A brief description of the contents
                of the packet. Empty string if not available.

        """
        implemented = "{}: found packet type {} at index {} '{}'"
        unimplemented = "{}: undecoded packet type : {} at index {} '{}'"
        no_subtype = "{}: missing subtype : type {} at index {} '{}'"
        no_type = "{}: missing type : type {} at index {} '{}'"

        # Packet location in Pcap or sequential number it was recieved at.
        index = int(self.packet.number) - 1

        if _type and _subtype and implemented:
            log_lvl = _logger.debug
            msg = implemented
        elif _type and _subtype:
            log_lvl = _logger.warning
            msg = unimplemented
        elif _type:
            log_lvl = _logger.warning
            msg = no_subtype
        else:
            log_lvl = _logger.warning
            msg = no_type

        try:
            packet_info = data_layer.get_field('')
            log_lvl(msg.format(
                self.process_id, _type, index, packet_info))
        except KeyError:
            packet_info = ''
            log_lvl(msg.format(
                self.process_id, _type, index, packet_info))

        return packet_info

    def store(self, packet, type_, subtype):
        """Store packets.

        Choose the function to store a given packet type.

        """
        data_layer = self.packet[self.packet.highest_layer.lower()]
        implemented = self.is_implemented(type_, subtype)

        self.get_packet_info(data_layer, type_, subtype, implemented)
        pkt = self.packet_factory.create(packet, type_, subtype)
        pkt.store(self.data_dir)


class PacketFactory:
    """Create packets.

    """
    @staticmethod
    def create(packet, type_, subtype):
        """Create a packet of the given type.

        """
        if type_ == 'GSM_A.CCCH' and subtype == '33':
            return PagePacket(packet)
        elif type_ == 'GSM_A.DTAP' and subtype == '30':
            return LACPacket(packet)
        else:
            return Packet(packet)


class Packet:
    """Gather packet generic GSMTAP information.

    """
    def __init__(self, packet):
        self.packet = packet

        # Packet Unique data for the type
        self.data_layer = self.packet[self.packet.highest_layer.lower()]

        # Prevent collisions when running multiple times on same capture file
        self.hash_ = hash((self.packet.__hash__(), time.time()))

        # Data common to all packets
        gsmtap_layer = self.packet['gsmtap']
        self.frame_nr = int(gsmtap_layer.frame_nr)
        self.channel = int(gsmtap_layer.chan_type)
        self.signal_dbm = float(gsmtap_layer.signal_dbm)
        self.arfcn = int(gsmtap_layer.arfcn)
        self.timestamp = float(self.packet.sniff_timestamp)

        people_time = str(datetime.datetime.fromtimestamp(self.timestamp)
                          .strftime('%Y-%m-%d%H:%M:%S'))

        self.datetime = people_time

    def store(self, database):
        """Store unimplemented packets which only have GSMTAP information.

        """
        conn = sqlite3.connect(database, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO PACKETS(
                UnixTime,
                PeopleTime,
                CHANNEL,
                DBM,
                ARFCN,
                FrameNumber,
                HASH
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.timestamp,
                self.datetime,
                self.channel,
                self.signal_dbm,
                self.arfcn,
                self.frame_nr,
                self.hash_
            )
        )
        conn.commit()
        conn.close()


class LACPacket(Packet):
    """Location Area Code (LAC) Packet.

    A packet with LAC, CID, and ARFCN data.

    """
    def __init__(self, packet):
        super().__init__(packet)
        self.cid = self.data_layer.gsm_a_lac
        self.lac = self.data_layer.gsm_a_bssmap_cell_ci

    def store(self, database):
        """Store packets with LAC and CID information.

        """
        conn = sqlite3.connect(database, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO LAC_CID(
                HASH,
                UnixTime,
                PeopleTime,
                CHANNEL,
                DBM,
                ARFCN,
                FrameNumber,
                LAC,
                CID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.hash_,
                self.timestamp,
                self.datetime,
                self.channel,
                self.signal_dbm,
                self.arfcn,
                self.frame_nr,
                self.lac,
                self.cid
            )
        )
        conn.commit()
        conn.close()


class PagePacket(Packet):
    """Location Area Code (LAC) Packet.

    A packet with LAC data.

    """
    def __init__(self, packet):
        super().__init__(packet)
        self.id_type = self.data_layer.gsm_a_ie_mobileid_type
        self.msg_type = self.data_layer.gsm_a_dtap_msg_rr_type
        self.mode = self.data_layer.gsm_a_rr_page_mode
        self.chan_req_ch1 = self.data_layer.gsm_a_rr_chnl_needed_ch1
        self.chan_req_ch2 = self.data_layer.gsm_a_rr_chnl_needed_ch2

    def store(self, database):
        """Store GSM_A.CCCH packets.

        Unique Inserts:
            * id_type
            * msg_type
            * mode
            * chan_req_ch1
            * chan_req_ch2

        """
        conn = sqlite3.connect(database, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO PAGE(
                HASH,
                UnixTime,
                PeopleTime,
                CHANNEL,
                DBM,
                ARFCN,
                FrameNumber,
                idType,
                msgType,
                MODE,
                reqChanOne,
                reqChanTwo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.hash_,
                self.timestamp,
                self.datetime,
                self.channel,
                self.signal_dbm,
                self.arfcn,
                self.frame_nr,
                self.id_type,
                self.msg_type,
                self.mode,
                self.chan_req_ch1,
                self.chan_req_ch2
            )
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    Decoder(0, 0)
