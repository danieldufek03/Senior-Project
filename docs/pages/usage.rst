=====
Usage
=====

Kivy arguments come first then antikythera's with ``--`` separating them::

    anti [kivy options] -- [antikythera options]

Kivy will start spinning up as soon as it is imported so if you ask for the antikythera help there will be some output before it is displayed and exits. Provide ``-h`` on either side to see the options available::

    anti -h         # display kivy options for the display
    anti -- -h      # display antikythera options the program

Run with very-verbose logging, a queue size of 1000 for incoming packets, and use a capture file for input::

    anti -- -vv -q 1000 -c tests/test_data/intercepting_catcher.pcap
