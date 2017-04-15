#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" gui.py

The GUI for antikythera

"""
import sys
import logging
import multiprocessing as mp

# Fix kivy's logging
import antikythera.kivylogs
from kivy.logger import Logger

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.graphics import *
from multiprocessing import Queue
from time import sleep

from kivy.uix.settings import SettingsWithSidebar

from antikythera import __version__
from antikythera.antikythera import __projectname__, __author__, __copyright__, __license__
from antikythera.antikythera import Anti, create_parser

_logger = logging.getLogger(__name__)

# Loads main from design file
Builder.load_file("mainscreen.kv")

# Color pallete (RGBA)
color_highlight = [0xAD/255, 0xD8/255, 0xE6/255, 0.5] # Blue highlight

class DefconLevel(GridLayout):

    def setHighlight(self, toggle):
        self.highlight = toggle

class Scanner(GridLayout):
    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)
        self.defconLevel = 0

        '''
        self.canvas.add(Color(rgba=self.color))
        self.canvas.add(Rectangle(pos=self.pos, size=self.size))
        '''

    # Called whenever itself or children are updated
    def do_layout(self, *args):
        super(Scanner, self).do_layout(*args)
        for child in self.children:
            if not isinstance(child, DefconLevel):
                continue

            # Creates new canvas
            child.canvas.before.clear()
            child.canvas.after.clear()

            with child.canvas.before:
                Color(rgba=child.color)
                Rectangle(pos=child.pos, size=child.size)

                if (child.level == self.defconLevel):
                    # Highlights
                    Color(rgba=color_highlight)
                    Rectangle(pos=child.pos, size=child.size)


            #child.canvas.add(rgba=child.color)
            #child.canvas.add(Rectangle(pos=child.pos, size=child.size))

            # Creates new label
            '''
            child.children.clear()

            with Label() as label:
                label.text = child.text
            '''

            child.label.text = child.text
            child.label.color = [0, 0, 0, 1]

            if (child.level == self.defconLevel):
                # Changes text color
                #child.label.color = [1, 1, 1, 1]

                iconSize = [child.height, child.height]
                iconPos = [child.pos[0] + (child.size[0] - child.height), child.pos[1]]

                with child.canvas.after:
                    # Meme icon
                    Color(rgba=[1, 1, 1, 1])
                    Rectangle(source=child.icon, pos=iconPos, size=iconSize)
                
                _logger.info("GUI: Updated threat level to {}".format(child.level))

            pass

    def update_defcon(self, level):
        """
        Updates threat level in GUI.
            int : level - Defcon level (1-5)
        """
        if (level is None or not isinstance(level, int) or level < 0 or level > 5):
            return

        self.defconLevel = level

        '''
        print("")
        for i in range(1, 6): # 1-5
            dLevel = eval("self.defconLevel" + str(level))
            #dLevel.highlight = (i == level)
            dLevel.setHighlight(i == level)

            if (i == level):
                #dLevel.highlight = True
                print("Set threat level", i)
        '''

        self.do_layout() # Re-draws GUI

        # _logger.info("GUI: Updated threat level")
        pass



class RootWidget(GridLayout):
    """

    """
    def start_detector(self):
        """

        """
        _logger.info("GUI: Starting detector")
        self.detecting()


    def detecting(self, *args):
        """

        """
        # TODO: Add stop scan functionality
        self.title.button_scan.text = "Stop Scan"
        self.title.button_scan.disabled = True

        '''
        # Remove start button and add status
        self.remove_widget(self.detect_button)
        self.status.text = ('Looking for a stingray...')
        '''

        xMax = self.scanner.anim_box.width * 0.8
        xMin = xMax * 0.3

        # Spinny Widget
        action_bar = Factory.AnimWidget()
        self.scanner.anim_box.add_widget(action_bar)
        animation = Animation(opacity=0.3, width=xMin, duration=0.6)
        animation += Animation(opacity=1, width= xMax, duration=0.8)
        animation.repeat = True
        animation.start(action_bar)


        '''
        # Scanning Label
        label = Label()
        self.scanner.anim_box.add_widget(action_bar)

        with label:
            font_size = 30
            text = "Scanning"
            color = [1, 1, 1, 1]
            halign = "center"
        '''


    def update_defcon(self, level):
        self.scanner.update_defcon(level)


    def update_status(self, new_text):
        self.status.text = new_text


class MetricDisplay(App):
    """

    """

    def __init__(self, *args, **kwargs):
        self.title = __projectname__
        super(MetricDisplay, self).__init__(*args, **kwargs)
        self.IMSI_detector = None
        self.timesUpdated = 0

    def on_start(self):
        """

        """
        parser = create_parser()
        args = parser.parse_args(sys.argv[1:])

        if args.loglevel:
            Logger.setLevel(level=args.loglevel)
        else:
            #loglevel = LOG_LEVELS.get(Config.get(['kivy', 'log_level']))
            Logger.setLevel(level=logging.WARNING)

        self.IMSI_detector = Anti(args.threads, args.headless, interface=args.interface, capturefile=args.pcap, max_qsize=args.qsize)



    def build(self):
        """

        """
        self.settings_cls = SettingsWithSidebar
        return RootWidget()

    def start(self):
        self.IMSI_detector.start()
        self.root.start_detector()


    def on_stop(self):
        """

        """
        if self.IMSI_detector.is_alive():
            _logger.info("GUI: Sending shutdown signal to Anti")
            self.IMSI_detector.shutdown()
            _logger.info("GUI: Joining Anti process {}".format(self.IMSI_detector.pid))
            self.IMSI_detector.join()
        _logger.info("GUI: Shutdown successfully".format(self.IMSI_detector.pid))

    def open_config(self):
        """
        Button - Open configuration settings
        """

        # Updates threat level
        self.timesUpdated += 1

        if self.timesUpdated > 5:
            self.timesUpdated = 1

        self.root.update_defcon(self.timesUpdated)

    def build_settings(self, settings):
        print("build_settings executed")
        json = '''
        [
            {
                "type": "string",
                "title": "Capture Interface",
                "desc": "Something Something Capture blah...",
                "section": "My Label",
                "key": "text"
            },
            {
                "type": "numeric",
                "title": "Label font size",
                "desc": "Choose the font size the label",
                "section": "My Label",
                "key": "font_size"
            }
        ]
        '''
        json2 = '''
        [
            {
                "type": "options",
                "title": "Capture Interface",
                "desc": "Determines network interface for packet capture",
                "section": "Finding Mr. Ray",
                "key": "text",
                "options": ["Pcap File", "Network"]
            }
        ]
        '''
        settings.add_json_panel('Finding Mr. Ray', self.config, data=json2)

    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Finding Mr. Ray', {'text': 'Pcap File'})

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            print("config change block entered")
            token = (section, key)
            if token == ('Finding Mr. Ray', 'Pcap File'):
                # Do the Pcap File things
                print('Capture interface moved to', value)
            elif token == ('Finding Mr. Ray', 'Network'):
                # Do the network capture things
                print('Capture interface moved to', value)

def run():
    """

    """
    _logger.info("GUI: Starting GUI App")
    MetricDisplay().run()
    return
    try:
        MetricDisplay().run()
    except Exception as e:
        _logger.info("GUI: Exception was thrown\n" + str(e))


if __name__ == "__main__":
    run()
