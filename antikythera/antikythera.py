#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" antikythera.py

The main program manager.

"""
import logging

from multiprocessing import Manager, Process, Pool, Queue

#from antikythera.gui import display
from antikythera.radio import radio
from antikythera.metrics import metrics

_logger = logging.getLogger(__name__)


class anti():
    """ Start the worker processes.

    """
    def __init__(self, num_processes, interface=None, capturefile=None):
        """

        """
        self.queue = Queue()
        self.NUMBER_OF_PROCESSES = num_processes
        self.workers = []
        self.interface = interface
        self.capturefile = capturefile
        _logger.info(self)

    def __str__(self):
        s = ("Initial Process Manager State:\n" +
             "Queue: {}\n".format(self.queue) +
             "Queue Size: {}\n".format(self.queue.qsize()) +
             "Number of Processes Initial: {}\n".format(self.NUMBER_OF_PROCESSES) +
             "Number of Processes Created: {}\n".format(len(self.workers)) +
             "Network Interface: {}\n".format(self.interface) +
             "Capture File: {}".format(self.capturefile)
            )
        return s


    def start(self):
        """

        """
        for i in range(self.NUMBER_OF_PROCESSES):
            _logger.info("Creating metric worker process".format(i))
            metric_worker = Process(target=metrics, args=(i + 2, self.queue))
            self.workers.append(metric_worker)

        _logger.info("Creating radio worker process")
        radio_worker = Process(target=radio, args=(1, self.queue))
        self.workers.append(radio_worker)

        #_logger.info("Creating GUI process")
        #gui_worker = Process(target=display, args=())
        #self.workers.append(gui_worker)

        for worker in self.workers:
            _logger.info("Starting process".format(worker))
            worker.start()


    def join(self):
        """

        """
        for worker in self.workers:
            _logger.info("Joining process".format(worker))
            worker.join()

if __name__ == '__main__':
    a = anti(0)
