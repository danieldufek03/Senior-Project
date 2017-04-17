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
    def __init__(self, process_id, q, *args, **kwargs):
        super(Decoder, self).__init__(*args, **kwargs)
        self.process_id = process_id
        self.q = q
        self.exit = mp.Event()

        self.datadir = appdirs.user_data_dir(__name__, __author__)
        self.conn = None
        self.c = None

    def run(self):
        """ Process main function, program loop.

        """
        _logger.debug("{}: Process started successfully".format(
            self.process_id))
        _logger.info("{}: Database storage set to {}".format(self.process_id,
                                                             self.datadir))
        self.create_tables()
        packet_manager = PacketManager(process_id, data_dir)
        while not self.exit.is_set():

            try:

                packet = self.q.get(timeout=10)
                _logger.debug("{}: Consumed packet Queue size is now {}".format(
                    self.process_id, self.q.qsize()))
                packet_manager.insert_packet(self.process_id, packet)


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

        self.c.execute('''CREATE TABLE IF NOT EXISTS PAGE(
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
        self.conn.close()


class PacketManager():
    """

    GSM_A.CCCH subtype 33:
        Paging type one

    """
    def __init__(self, process_id, data_dir):
        self.process_id = process_id
        self.data_dir = data_dir

        self.packet_types = {
            'GSM_A.CCCH': [33],
            'GSM_A.DTAP': []
        }

    def insert_packet(self, packet):
        """

        """
        self.packet = packet
        packet_type, packet_subtype = self.get_packet_type()
        data = self.decode_packet(packet_type, packet_subtype)
        self.store(data, packet_type, packet_subtype)

    def get_packet_type(self, process_id, packet):
        """

        """
        packet_type = packet.highest_layer
        if packet_type in self.packet_types.keys():

            if 'gsm_a_dtap_msg_rr_type' in packet[packet.highest_layer.lower()]:
                packet_subtype = int(
                    packet[packet.highest_layer.lower()].gsm_a_dtap_msg_rr_type
                )
            else:
                _logger.warning("{}: unimplemented packet subtype {} at index {}".format(
                    self.process_id, packet_type, (int(packet.number) - 1)))
                return (packet_type, None)

            if packet_subtype in self.packet_types[packet_type]:
                return (packet_type, packet_subtype)

        else:
            _logger.warning("{}: unimplemented packet type {} at index {}".format(
                self.process_id, packet_type, (int(packet.number) - 1)))
            return (packet_type, None)
    """
        if packet.__repr__() == '<UDP/GSM_A.CCCH Packet>':
            if packet['gsm_a.ccch'].gsm_a_dtap_msg_rr_type == '33':
                _logger.debug("{}: decoding packet type {}".format(
                    self.process_id, packet.__repr__()))
                self.decode_paging(packet, data)
                self.store_paging(packet, data)
            else:
                _logger.warning("{}: Packet decode not implemted {} Type {}"
                                .format(self.process_id,
                                        packet.__repr__(),
                                        packet['gsm_a.ccch'].gsm_a_dtap_msg_rr_type))
        else:
            if packet.layers[-1].__repr__() == '<GSM_A.DTAP Layer>':
                try:
                    _logger.warning("{}: unimplemented packet type '{}' at index {}".format(
                        self.process_id, packet['gsm_a.dtap']._all_fields[''], (int(packet.number) - 1)))
                    self.store_packet(packet, data)
                except KeyError:
                    _logger.warning("{}: unable to get layer type for unimplemented packet type '{}' at index {}".format(
                        self.process_id, packet.__repr__(), (int(packet.number) - 1)))
                    self.store_packet(packet, data)
        return packet_type
    """

    def decode_packet(self, packet_type, packet_subtype):
        """ Get only the needed attributes from the packet.

        """
        _logger.debug("{}: Decoding packet {}".format(
            self.process_id, packet['gsmtap'].frame_nr))

        data = {}

        # Prevent collisions when running multiple times on same capture file
        data.update({"hash": hash((self.packet.__hash__(), time.time()))})

        # Layer common to all packets
        data.update({"frame_nr": float(self.packet['gsmtap'].frame_nr)})
        data.update({"channel": float(self.packet['gsmtap'].chan_type)})
        data.update({"signal_dbm": float(self.packet['gsmtap'].signal_dbm)})
        data.update({"arfcn": float(self.packet['gsmtap'].arfcn)})
        data.update({"timestamp": float(self.packet.sniff_timestamp)})
        data.update({"datetime":
                            str(datetime.datetime.fromtimestamp(
                                data['timestamp']).strftime(
                                    '%Y-%m-%d%H:%M:%S'))})

        if packet_type == 'GSM_A.CCCH' and packet_subtype == 33:
            self.decode_paging(data)

        # Detect packet type and extract needed data
        return data

    def decode_paging(self, data):
        """ Decode paging packets.

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

    def decode_system(self, packet, data):
        """ Decode system packets.

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

        ===========================================

        # Mobile ID Type
        data.update({"id_type": float(
            packet['gsm_a.ccch'].gsm_a_ie_mobileid_type)})

        # Message Type
        data.update({"msg_type": float(
            packet['gsm_a.ccch'].gsm_a_dtap_msg_rr_type)})

        # Page Mode
        data.update({"mode": float(
            packet['gsm_a.ccch'].gsm_a_rr_page_mode)})

        # Channel Requests
        data.update({"chan_req_ch1": float(
            packet['gsm_a.ccch'].gsm_a_rr_chnl_needed_ch1)})
        data.update({"chan_req_ch2": float(
            packet['gsm_a.ccch'].gsm_a_rr_chnl_needed_ch2)})
        """
        pass

    def store_paging(self, data):
        """ Decode GSM_A.CCCH packets.

        Unique Inserts:
            * id_type
            * msg_type
            * mode
            * chan_req_ch1
            * chan_req_ch2

        """
        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute(
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

    def store_packet(self, data):
        """ Put packet into database.

        """
        _logger.debug("{}: Storing packet {}"
                      .format(self.process_id, self.packet['gsmtap'].frame_nr))

        self.conn = sqlite3.connect(self.datadir, check_same_thread=False)
        self.c = self.conn.cursor()
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
        self.conn.commit()
        self.conn.close()

    def store(self, data, packet_type, packet_subtype):
        if packet_type == 'GSM_A.CCCH' and packet_subtype == 33:
            store_paging(data)
        else:
            store_packet(data)


if __name__ == "__main__":
    Decoder(0, 0)
