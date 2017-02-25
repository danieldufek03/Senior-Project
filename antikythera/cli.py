#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" antikythera.py

This is the Antikythera console script.

To run this script uncomment the following line in the
entry_points section in setup.cfg:

    console_scripts =
        hello_world = antikythera.module:function

Then run `python setup.py install` which will install the command `hello_world`
inside your current environment.

Todo:
    * Add Windows logging

"""
import os
import sys
import argparse
import logging

from antikythera import __version__

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
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list

    """
    _logger.debug("Starting main()")
    args = parse_args(args)

    # Setup logs
    if args.debug:
        loglevel = "DEBUG"
    else:
        loglevel = args.log
    setup_logs(loglevel)

    if args.verbose:
        print("[*] Verbose")

    print("[*] Threads".format(args.threads))

    if args.capture is not None:
        print("[*] Input Source:".format(args.capture))
    else:
        print("[*] Input Source:".format(args.interface))
    

    _logger.debug("All done, shutting down.")
    logging.shutdown()



def parse_args(args):
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
        const=1,
        help="Number of threads to use.",
        action='store'),
    parser.add_argument(
        '-v',
        '--verbose',
        help="Increase verbosity of output.",
        action='store_true'),
    logs.add_argument(
        '-d',
        '--debug',
        help="Set logging level to DEBUG.",
        action='store_true'),
    logs.add_argument(
        '-l',
        '--log',
        nargs='?',
        type=str,
        default='INFO',
        help="Set logging level, defaults to INFO.",
        action='store'),
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

    return parser.parse_args(args)


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
    logfile = logdir + "log.txt"

    # Convert `logging' string to a level that can be set
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('[*] Invalid log level: {}'.format(loglevel))
    logging.basicConfig(level=numeric_level, filename=logfile, filemode='w')

    # create file handler which logs messages
    fh = logging.FileHandler('../main.log')
    fh.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)


def run():
    """ Entry point for console_scripts.

    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
