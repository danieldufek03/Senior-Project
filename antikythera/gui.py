#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" gui.py

The GUI for antikythera

"""
import logging

from kivy.app import App
from kivy.uix.button import Button
from kivy.logger import Logger

logging.Logger.manager.root = Logger
_logger = logging.getLogger(__name__)

class MetricDisplay(App):
    def build(self):
        return Button(text="Find a Stingray!",
                      background_color=(1, 0.125, 0.321, 1),
                      background_normal='',
                      font_size=100)


def run():
    MetricDisplay().run()

if __name__ == "__main__":
    run()
