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
    def __init__(self, process_id, queue, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.queue = queue
        self.exit = mp.Event()

        self.data_dir = appdirs.user_data_dir("anti.sqlite3", "anything")

    def run(self):
        """ Process main function, program loop.

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
        _logger.info("{}: Recieved shutdown command".format(self.process_id))
        self.exit.set()

    def create_tables(self):
        """ Create packet tables.

        Unique entries:
            * id_type
            * msg_type
            * mode
            * chan_req_ch1
            * chan_req_ch2

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


class PacketManager():
    """Manage operations on packets.

    """
    def __init__(self, process_id, data_dir):
        self.process_id = process_id
        self.data_dir = data_dir

        self.packet_types = {
            'GSM_A.CCCH': ['33'],
            'GSM_A.DTAP': ['30']
        }

    def insert_packet(self, packet):
        """Insert only needed data into the database for analysis.

        """
        self.packet = packet
        packet_type, packet_subtype = self.get_packet_type()
        data = self.decode_packet(packet_type, packet_subtype)
        self.store(data, packet_type, packet_subtype)

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

    def decode_packet(self, packet_type, packet_subtype):
        """Get only the needed attributes from the packet.

        First the GSMTAP layer is handled which is universal across all
        packets. Then the specific decoder functions for the packets type
        and subtype are called.

        """

        data = {}

        # Prevent collisions when running multiple times on same capture file
        data.update({"hash": hash((self.packet.__hash__(), time.time()))})

        # Layer common to all packets
        data.update({"frame_nr": float(self.packet['gsmtap'].frame_nr)})
        data.update({"channel": float(self.packet['gsmtap'].chan_type)})
        data.update({"signal_dbm": float(self.packet['gsmtap'].signal_dbm)})
        data.update({"arfcn": float(self.packet['gsmtap'].arfcn)})
        data.update({"timestamp": float(self.packet.sniff_timestamp)})

        people_time = str(datetime.datetime.fromtimestamp(data['timestamp'])
                          .strftime('%Y-%m-%d%H:%M:%S'))

        data.update({"datetime": people_time})

        if packet_type == 'GSM_A.CCCH' and packet_subtype == '33':
            self.decode_paging(data)
        if packet_type == 'GSM_A.DTAP' and packet_subtype == '30':
            self.decode_system(data)

        # Detect packet type and extract needed data
        return data

    def decode_paging(self, data):
        """Decode paging packets.

        Adds data only specific to the CCCH packets.

        Pyshark codes:
            * Page Mode:
                * 0 = Normal
            * Channel Request One/Two
                * 0 = Unspecified
            * Mobile ID Type
                * 0 = Unspecified
            * Message Type
                * 33 = Page Mode One

        """
        # Mobile ID Type
        data.update({"id_type": float(
            self.packet['gsm_a.ccch'].gsm_a_ie_mobileid_type)})

        # Message Type
        data.update({"msg_type": float(
            self.packet['gsm_a.ccch'].gsm_a_dtap_msg_rr_type)})

        # Page Mode
        data.update({"mode": float(
            self.packet['gsm_a.ccch'].gsm_a_rr_page_mode)})

        # Channel Requests
        data.update({"chan_req_ch1": float(
            self.packet['gsm_a.ccch'].gsm_a_rr_chnl_needed_ch1)})
        data.update({"chan_req_ch2": float(
            self.packet['gsm_a.ccch'].gsm_a_rr_chnl_needed_ch2)})

    def decode_system(self, data):
        """Decode system packets.

        Decodes data only data specific to the system packets.

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
        data.update({"lac": int(
            self.packet['gsm_a.dtap'].gsm_a_lac)})

        data.update({"cell_id": int(
            self.packet['gsm_a.dtap'].gsm_a_bssmap_cell_ci)})

    def store_paging(self, data):
        """Store GSM_A.CCCH packets.

        Unique Inserts:
            * id_type
            * msg_type
            * mode
            * chan_req_ch1
            * chan_req_ch2

        """
        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
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
                data['hash'],
                data['timestamp'],
                data['datetime'],
                data['channel'],
                data['signal_dbm'],
                data['arfcn'],
                data['frame_nr'],
                data['id_type'],
                data['msg_type'],
                data['mode'],
                data['chan_req_ch1'],
                data['chan_req_ch2']
            )
        )
        conn.commit()
        conn.close()

    def store_system(self, data):
        """Store GSM_A.DTAP packets.

        Unique Inserts:
            * lac
            * cid

        """
        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO SYSTEM(
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
                data['hash'],
                data['timestamp'],
                data['datetime'],
                data['channel'],
                data['signal_dbm'],
                data['arfcn'],
                data['frame_nr'],
                data['lac'],
                data['cell_id']
            )
        )
        conn.commit()
        conn.close()

    def store_packet(self, data):
        """Store unimplemented packets which only have GSMTAP information.

        """
        _logger.trace("{}: Storing packet {}"
                      .format(self.process_id, self.packet['gsmtap'].frame_nr))

        conn = sqlite3.connect(self.data_dir, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
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
                data['timestamp'],
                data['datetime'],
                data['channel'],
                data['signal_dbm'],
                data['arfcn'],
                '123456789012345',
                '324345566767899',
                '303',
                '151515',
                '131313',
                '02',
                '1234567891234567',
                data['frame_nr'],
                data['hash']
            )
        )
        conn.commit()
        conn.close()

    def store(self, data, packet_type, packet_subtype):
        """Store packets.

        Choose the function to store a given packet type.

        """

        data_layer = self.packet[self.packet.highest_layer.lower()]

        if packet_type == 'GSM_A.CCCH' and packet_subtype == '33':
            self.get_packet_info(data_layer, packet_type, packet_subtype, True)
            self.store_paging(data)
        elif packet_type == 'GSM_A.DTAP' and packet_subtype == '30':
            self.get_packet_info(data_layer, packet_type, packet_subtype, True)
            self.store_system(data)
        else:
            self.get_packet_info(data_layer, packet_type, packet_subtype, False)
            self.store_packet(data)

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


if __name__ == "__main__":
    Decoder(0, 0)
