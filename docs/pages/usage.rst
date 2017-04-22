=====
Usage
=====

Overview
========

Kivy arguments come first then antikythera's with ``--`` separating them::

    anti [kivy options] -- [antikythera options]

Kivy will start spinning up as soon as it is imported so if you ask for the antikythera help there will be some output before it is displayed and exits. Provide ``-h`` on either side to see the options available::

    anti -h         # display kivy options for the display
    anti -- -h      # display antikythera options the program

Run with very-verbose logging, a queue size of 1000 for incoming packets, and use a capture file for input::

    anti -- -vv -q 1000 -c tests/test_data/intercepting_catcher.pcap


Options
=======

Kivy
----

Kivy Usage::

    anti [OPTION...]

-h, --help
    Prints this help message.
-d, --debug
    Shows debug log.
-a, --auto-fullscreen
    Force 'auto' fullscreen mode (no resolution change).
    Uses your display's resolution. This is most likely what you want.
-c, --config 
    Set a custom [section] key=value in the configuration object. Example: --config section:key[:value]
-f, --fullscreen
    Force running in fullscreen mode.
-k, --fake-fullscreen
    Force 'fake' fullscreen mode (no window border/decoration).
    Uses the resolution specified by width and height in your config.
-w, --windowed
    Force running in a window.
-p, --provider
    Add an input provider (eg: ccvtable1:tuio,192.168.0.1:3333). Example: --provider id:provider[,options]
-m mod, --module=mod
    Activate a module (use "list" to get a list of available modules).
-r, --rotation
    Rotate the window's contents (0, 90, 180, 270).
-s, --save
    Save current Kivy configuration.
--size=AxB
    Size of window geometry. Example: --size=640x480
--dpi=x
    Manually overload the Window DPI (for testing only.) Example: --dpi=96


Antikythera
-----------

Anti Usage::

    anti [-h] [-t [THREADS]] [-q [QSIZE]] [--headless] [-v | -vv | -vvv] -c [PCAP] | -i [INTERFACE]]

-h, --help            show this help message and exit
-t, --threads
                    Number of threads to use.
-q, --qsize
                    The maximum queue size for packets waiting to be
                    processed.
--headless            Run in headless mode without GUI.
-v, --verbose         set loglevel to INFO
-vv, --very-verbose   set loglevel to DEBUG
-vvv, --trace         set loglevel to TRACE
-c, --capture
                    Path to a capture file to use as input.
-i, --interface
                    The identifier of the network interface to use.
