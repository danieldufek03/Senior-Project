#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" gui.py

The GUI for antikythera

"""
import sys
import logging

# Fix kivy's logging
import antikythera.kivylogs
from kivy.logger import Logger

from kivy.app import App
from kivy.uix.button import Button

from antikythera import __version__
from antikythera.antikythera import anti, create_parser

_logger = logging.getLogger(__name__)

__author__= "Finding Ray"
__copyright__ = "Finding Ray"
__license__ = "GNU GPLv3+"


class MetricDisplay(App):
    """

    """
    def build(self):
        """

        """
        return Button(text="Find a Stingray!",
                      background_color=(1, 0.125, 0.321, 1),
                      background_normal='',
                      font_size=100)


def run():
    """

    """
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.loglevel:
        Logger.setLevel(level=args.loglevel)
    else:
        #loglevel = LOG_LEVELS.get(Config.get(['kivy', 'log_level']))
        Logger.setLevel(level=logging.WARNING)

    _logger.debug("Passing args to detector")
    IMSI_detector = anti(args.threads, args.headless, interface=args.interface, capturefile=args.pcap, max_qsize=args.qsize)
    _logger.info("Starting detector")
    IMSI_detector.start()

    _logger.info("Starting GUI")
    MetricDisplay().run()


if __name__ == "__main__":
    run()
