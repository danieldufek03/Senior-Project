import time
import sys
import os
import logging
import threading

location = input("coordinates?")   
defcon = int(input("defcon level?"))
if defcon > 5 or defcon < 1:
	print("Invalid defcon level, try again")
	exit()
if defcon == 5:
	meaning = "History mismatch"
if defcon == 4:
	meaning = "Unusual signal strength"
if defcon == 3:
	meaning = "Unusual signal strength & history mismatch"
if defcon == 2:
	meaning = "Incorrect area code"
if defcon == 1:
	meaning = "Unusual signal strength, history mismatch, incorrect area code"
	 
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s ',
                    datefmt='[%b %d %H:%M:%S %Y]',
                    filename='logfile.log')
    # define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
    # set a format which is simpler for console use
formatter = logging.Formatter('%(message)s')
    # tell the handler to use this format
console.setFormatter(formatter)
    # add the handler to the root logger
logging.getLogger('').addHandler(console)
    # Now, we can log to the root logger, or any other logger. First the root...
#logging.info('Server_DR information')
    #loggers needed to make log entries 
logger1 = logging.getLogger()

logger1.info("[%s] Level %s Event: %s", location, defcon, meaning)
