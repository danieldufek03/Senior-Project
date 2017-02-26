#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" cli.py

This is the Antikythera console script. It provides the
entry points that are used to run the program when it is
installed. To install the program run ``python setup.py install``
and it will be installed on the system.

"""
import os
import sys
import argparse
import logging

from antikythera import __version__
from antikythera.antikythera import anti

try:
    import appdirs
except ImportError as e:
    print("{}\nMaybe try `pip install -r requirements.txt'".format(e))
    sys.exit(1)

__author__= "Finding Ray"
__copyright__ = "Finding Ray"
__license__ = "GNU GPLv3+"
_logger = logging.getLogger(__name__)

def main(args):
    """Main entry point allowing external calls.

    Collects command line arguments, sets up the logs, and logs information
    about them. Then it starts the program loop.

    Args:
      args ([str]): command line parameter list

    """
    parser = create_parser()
    args = parser.parse_args(args)

    # Set up logs, default to warning
    if args.loglevel:
        setup_logs(args.loglevel)
    else:
        setup_logs(logging.WARNING)

    # Save input parameters to logfile and set them
    _logger.info("Starting gathered arguments, setting them")
    _logger.info("Threads Requested: {}".format(args.threads))
    if args.capture is not None:
        _logger.info("Input Source: {}".format(args.capture))
        if args.qsize is not None:
            IMSI_detector = anti(args.threads, capturefile=args.capture, max_qsize=args.qsize)
        else:
            IMSI_detector = anti(args.threads, capturefile=args.capture)
    else:
        _logger.info("Input Source: {}".format(args.interface))
        if args.qsize is not None:
            IMSI_detector = anti(args.threads, interface=args.interface, max_qsize=args.qsize)
        else:
            IMSI_detector = anti(args.threads, interface=args.interface)

    # Start Subprocesses
    _logger.info("Setup complete starting program")
    IMSI_detector.start()

    # Wait
    IMSI_detector.join()
    
    _logger.info("All done, shutting down.")
    logging.shutdown()



def create_parser():
    """ Parse command line parameters.

    :return: command line parameters as :obj:`argparse.Namespace`
    Args:
        args ([str]): List of strings representing the command line arguments.

    Returns:
        argparse.Namespace: Simple object with a readable string
        representation of the argument list.

    """
    parser = argparse.ArgumentParser(
        description="IMSI Catcher Detector.")
    source=parser.add_mutually_exclusive_group()
    logs=parser.add_mutually_exclusive_group()
    parser.add_argument(
        '-t',
        '--threads',
        nargs='?',
        type=int,
        default=1,
        help="Number of threads to use.",
        action='store'),
    parser.add_argument(
        '-q',
        '--qsize',
        nargs='?',
        type=int,
        default=None,
        help="The maximum queue size for packets waiting to be processed.",
        action='store'),
    logs.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    logs.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    source.add_argument(
        '-c',
        '--capture',
        nargs='?',
        type=str,
        default=None,
        help="Path to a capture file to use as input.",
        action='store'),
    source.add_argument(
        '-i',
        '--interface',
        nargs='?',
        type=str,
        default=None,
        help="The identifier of the network interface to use.",
        action='store')

    return parser


def setup_logs(loglevel):
    """ Set up logger to be used between all modules.

    Set logging root and file handler configuration to default to
    ``INFO`` and write output to ``main.log``. Set console
    handler to default to ``INFO``.

    Args:
        loglevel str: A string of one of the Default Python logging levels.
            See the `Python logging level documentation <https://docs.python.org/3/howto/logging.html#logging-levels>`_
            for more information.

    """
    logdir = appdirs.user_log_dir(__name__, __author__)
    if not os.path.exists(logdir):
        try:
            os.makedirs(logdir)
        except OSError as e:
            print("{}".format(e))
    logfile = logdir + ".txt"
    print("[*] Logfile: {}".format(logfile))

    # Convert `logging' string to a level that can be set
    logging.basicConfig(level=loglevel, filename=logfile, filemode='w')

    # create file handler which logs messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(loglevel)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)


def run():
    """ Entry point for console_scripts.

    """
    main(sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(run())
