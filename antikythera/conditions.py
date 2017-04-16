#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

Pull variables from db, if any variable contains data then set corresponding 
variable equal to one.  follow through till all 

'''
import sys
import logging
import sqlite3
import datetime
import appdirs
import random
import time
import multiprocessing as mp

from multiprocessing import Process, Queue
'''
import antikythera.kivylogs
from kivy.logger import Logger

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.gridlayout import GridLayout
from multiprocessing import Queue
from time import sleep


from antikythera import __version__
from antikythera.antikythera import Anti, create_parser
'''


_logger = logging.getLogger(__name__)

__author__= "TeamAwesome"

TMSI   = random.randint(0,1)
IMSI   = random.randint(0,1)
LAC    = random.randint(0,1)
CID    = random.randint(0,1)
MCC    = random.randint(0,1)
MNC    = random.randint(0,1)
IMEISV = random.randint(0,1)

#class DEFCON_Conditions(process):
#"""
#Conditions that need to be meet before a DEFCON level is determined.
#"""
def check_defcon(TMSI, IMSI, LAC, CID, MCC, MNC, IMEISV):
	temp = TMSI + IMSI + LAC + CID + MCC + MNC + IMEISV
	if  temp >= 7:
		defcon = 1
	elif  temp >= 5 and temp < 7:
		defcon = 2
	elif  temp >= 3 and temp < 5:
		defcon = 3
	elif  temp >= 1 and temp < 3:
		defcon = 4
	elif  temp < 1:
		defcon = 5
	else:
		print('Defcon either undetermined or already at lowest level')
	return defcon

def print_defcon(defcon):
	if defcon == 1:
#insert command to flash defcon 1 button gui
		print("""Defcon level 1 has been set, you are advised turn
all devices off and vacate the area immediately""")
	elif defcon == 2:
		print("""Defcon level 2 has been set, you are advised turn
all devices off and take countermeasures for an attack""")
	elif defcon == 3:
		print("""Defcon level 3 has been set, you are advised to analyze 
your surroindings and take precautonary procedures""")
	elif defcon == 4:
		print("""Defcon level 4 has been set, you are in the vacinity
of a StingRay and susceptible to an attack""")
	elif defcon == 5:
		print("""Defcon level 5 has been set, you are not in any
immediate danger or threat of a StingRay""")
	else:
		print('No Stingrays Detected')

def start():
#_logger.info("GUI: Starting GUI App")
#MetricDisplay().run()
	defcon = check_defcon(TMSI, IMSI, LAC, CID, MCC, MNC, IMEISV)
	print_defcon(defcon)

if __name__ == "__main__":
	start()
