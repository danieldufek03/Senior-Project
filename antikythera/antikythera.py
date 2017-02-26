#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" antikythera.py

The main program manager.

"""
import logging

from multiprocessing import Manager, Process, Pool, Queue

from antikythera.radio import radio
from antikythera.metrics import metrics

_logger = logging.getLogger(__name__)


class anti():
    """ Start the worker processes.

    """
    def __init__(self, num_processes, headless, interface=None,
                 capturefile=None, max_qsize=100000):
        """

        """
        self.MAX_QUEUE_SIZE = max_qsize
        self.queue = Queue(self.MAX_QUEUE_SIZE)
        self.NUMBER_OF_PROCESSES = num_processes
        self.workers = []
        self.interface = interface
        self.capturefile = capturefile
        self.headless = headless
        _logger.info(self)

    def __str__(self):
        s = ("Initial Process Manager State:\n" +
             "[*] Headless: {}\n".format(self.headless) +
             "[*] Queue: {}\n".format(self.queue) +
             "[*] Queue Size: {}\n".format(self.queue.qsize()) +
             "[*] Max Queue Size: {}\n".format(self.MAX_QUEUE_SIZE) +
             "[*] Number of Processes to Create: {}\n".format(self.NUMBER_OF_PROCESSES) +
             "[*] Number of Processes Created: {}\n".format(len(self.workers)) +
             "[*] Network Interface: {}\n".format(self.interface) +
             "[*] Capture File: {}".format(self.capturefile)
            )
        return s


    def start(self):
        """

        """
        for i in range(self.NUMBER_OF_PROCESSES):
            name = "metric-" + str(i)
            _logger.info("Creating metric process: {}".format(name))
            metric_worker = Process(target=metrics, name=name, args=(name, self.queue))
            self.workers.append(metric_worker)

        _logger.info("Creating radio process: radio")
        radio_worker = Process(target=radio, name="radio", args=("radio", self.queue))
        self.workers.append(radio_worker)

        if not self.headless:
            from antikythera.gui import run
            _logger.info("Creating GUI process: gui")
            gui_worker = Process(target=run, name="gui", args=())
            self.workers.append(gui_worker)
        else:
            _logger.info("Running in headless mode.")

        for worker in self.workers:
            _logger.info("Starting process: {}".format(worker))
            worker.start()


    def join(self):
        """

        """
        for worker in self.workers:
            _logger.info("Joining process: {}".format(worker))
            worker.join()

if __name__ == '__main__':
    a = anti(0)
