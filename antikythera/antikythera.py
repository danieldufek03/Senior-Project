#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" antikythera.py

The main program loop.

"""
import sys
import logging

from threading import Thread
from queue import Queue

#from antikythera.gui import display
from antikythera.radio import radio
from antikythera.metrics import metrics

_logger = logging.getLogger(__name__)


def anti(num_threads, interface=None, capturefile=None):
    """ Start the worker threads.

    """
    q = Queue()
    threads = []
    
    #_logger.debug("Creating radio worker thread 0")
    #gui_worker = Thread(target=display, args=())
    #gui_worker.setDaemon(False)
    #threads.append(gui_worker)

    _logger.debug("Creating radio worker thread 1")
    radio_worker = Thread(target=radio, args=(1, q))
    radio_worker.setDaemon(True)
    threads.append(radio_worker)

    for thread_id in range(num_threads):
        _logger.debug("Creating metric worker thread {}".format(thread_id))
        metric_worker = Thread(target=radio, args=(thread_id + 2, q))
        metric_worker.setDaemon(True)
        threads.append(metric_worker)

    for thread in threads:
        _logger.debug("Starting thread {}".format(thread))
        thread.start()

    for thread in threads:
        _logger.debug("Joining thread {}".format(thread))
        thread.join()
