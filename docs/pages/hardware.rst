========
Hardware
========

This documents the hardware assembly used to test the applications ability to run in an embedded environment on a small portable device as well as the touchscreen user interface. There are much better software defined radios available some of which that also work are listed below.

Components
==========

*   `Raspberry Pi 3 - Model B (~$35) <https://www.adafruit.com/products/3055>`_
*   `Pi Foundation Display - 7" Touchscreen (~$75) <https://www.adafruit.com/products/2718>`_
*   `RTL-SDR with E4000 Tuner ($20-$40) <https://www.amazon.com/RTL-SDR-Elonics-Aluminum-Enclosure-0-5PPM/dp/B01K10R2YK/ref=sr_1_14?ie=UTF8&qid=1480875208&sr=8-14&keywords=rtl-sdr>`_
*   `PowerBoost 1000 ($20) <https://www.adafruit.com/product/2465>`_
*   `Lithium Ion Polymer Battery - 3.7v 2500mAh ($15) <https://www.adafruit.com/products/328>`_
*   `Latching or Toggle switch (~$7) <https://www.amazon.com/WerFamily-Indicator-Waterproof-Stainless-Self-locking/dp/B013ET18X6/ref=sr_1_16?ie=UTF8&qid=1480877707&sr=8-16&keywords=latching%2Bpush%2Bbutton&th=1>`_
*   `Right-angle Mini GSM/Cellular Quad-Band Antenna - 2dBi SMA Plug ($5) <https://www.adafruit.com/products/1858>`_


|    Total ~$200


.. node::

    The total cost is not reflective of the cost of a final product, most of the price is
    paying for prototyping convenience. Cheaper and even better hardware exists but
    without such a huge support community and already made tools, 3D models, etc.

|
|

Tools & Consumables
===================

*   Must haves
  
    *   3D Printer
    *   Soldering Iron
    *   Screwdriver (including a long narrow jewelers)
    *   Wire Strippers
    *   Filament (ABS, PLA, etc.)
    *   `Solder <https://www.adafruit.com/products/1930>`_
    *   `SMA Male to Female Coaxial Cable with Nut Bulkhead Crimp <https://www.amazon.com/DLFPV%C2%AE-Antenna-Extension-Connector-Pigtail/dp/B01KO1L92C/ref=sr_1_7?ie=UTF8&qid=1480877550&sr=8-7&keywords=SMA+Pigtail>`_
    *   `26 AWG Silicone Cover Stranded-Core Wire <https://www.adafruit.com/products/1858?q=26%20awg&>`_
    *   `M2.5 x 4mm screws for display mount <https://www.amazon.com/M2-5-4mm-Button-Head-Screw/dp/B00B845BGK/ref=sr_1_1?s=toys-and-games&ie=UTF8&qid=1480886284&sr=1-1&keywords=m2.5+x+4mm>`_
    *   `M3 x 4mm screws <https://www.amazon.com/Team-Associated-91158-4mm-Screw/dp/B005EDIOW4/ref=sr_1_3?s=toys-and-games&ie=UTF8&qid=1480886513&sr=1-3&keywords=m3+x+4mm>`_

*   Nice to have

    *   Multimeter
    *   Heat Gun
    *   Heat Shrink (For 26 AWG)

|
|

Case Files Changelog
====================

*   :download:`Spacers <stl/spacer.stl>`
*   :download:`Case Revision Zero <stl/pi_display_r0.stl>`

    *   Original File

*   :download:`Case Revision One <stl/pi_display_r1.stl>`

    *   Remove external ports
    *   Make case symmetrical

*   :download:`Case Revision Two <stl/pi_display_r2.stl>`

    *   Add latching power switch port
    *   Add SMA coaxial pigtail port
    *   Add long team name

*   :download:`Case Revision Three <stl/pi_display_r3.stl>`

    *   Add mount for power regulator and charger
    *   Add panel mount USB ports
    *   Change team name to short name
    *   Make team name letters deeper
    *   Make team name letters larger

|
|

Assembly
========

.. image:: dia/hacks_circuit-diagram-text.png

|
|

Other Hardware of Note
======================

*   `HackRF One (~$320) <https://greatscottgadgets.com/hackrf/>`_
*   `Blade RF (~$420) <http://nuand.com/>`_
*   `USRP Bus Series (~$700) <https://www.ettus.com/product/category/USRP-Bus-Series>`_

|
|

Special Thanks
==============

*   `Adafruit for their Pi tablet article <https://learn.adafruit.com/7-portable-raspberry-pi-multitouch-tablet/overview>`_
*   `CdnReprap for the original case STL <http://www.thingiverse.com/thing:1803757>`_
