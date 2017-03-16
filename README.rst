===========
antikythera
===========

.. image:: https://gitlab.com/finding-ray/antikythera/badges/master/build.svg
    :target: https://gitlab.com/finding-ray/antikythera/pipelines
    :width: 10%
.. image:: https://gitlab.com/finding-ray/antikythera/badges/master/coverage.svg
    :target: https://finding-ray.gitlab.io/antikythera/htmlcov/index.html
    :width: 10%
.. image:: https://badge.fury.io/py/antikythera.svg
    :target: https://pypi.python.org/pypi/antikythera
    :width: 10%
.. image:: https://img.shields.io/badge/Development-Alpha-ff2052.svg
    :width: 10%

``antikythera`` is the software component of the IMSI-Catcher Detector device Finding Ray. It is built with Python to catch `IMSI-Catchers <https://en.wikipedia.org/wiki/IMSI-catcher>`_, also known as Stingrays, Dirtboxes, or malicious base stations. IMSI-Catchers are used globally by many police departments to spy on citizens, organizations for corporate espionage, and other malicious actors seeking to Man-in-The-Middle (MiTM) cellular communications.

Antikythera is:

*  Designed to be usable on Windows, Linux, and OSX.
*  Capable of running on both x86 and ARM architectures (PCs, Android, iPhone, RaspberryPi, etc.)
*  Built to run without a lot of resources in an embedded environment.
*  Uses a software defined radio.


But most importantly it is not yet as advanced or reliable as `SnoopSnitch <https://opensource.srlabs.de/projects/snoopsnitch>`_ and `AIMSICD <https://github.com/CellularPrivacy/Android-IMSI-Catcher-Detector>`_. Both of which have also provided invaluable documentation allowing for this project to exist and attempt to provide an IMSI-Catcher detector that is not required to be a phone.

Quick Install
=============

To install first ensure Tshark the command line utility for Wireshark is installed, see the `wireshark documentation <https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallWinInstall.html>`_ for information on Windows setup or run ``apt-get install tshark`` on Linux. Then install with pip::

    pip install antikythera

Development Environment Setup
=============================

Windows
-------

Wireshark must be installed for the ``pyshark`` library to have access to the packet dissectors it needs. See the `Wireshark Documentation <https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallWinInstall.html>`_ for details.

Linux
-----

Setup a virtual environment to ensure system packages are not used::

    mkdir -p ~/.virtualenv/antikythera
    python3 -m venv ~/.virtualenv/antikythera
    source ~/.virtualenv/antikythera/bin/activate

.. note::

    The command ``source ~/.virtualenv/antikythera/bin/activate`` must
    be reran for each new shell instance. When activated the name of the
    virtual environment should appear somewhere on the prompt such as::

        (antikythera) user@hostname:~$

Then for Debian or Ubuntu based distributions just run the setup
script ``sudo bash setup.sh``. The documentation can be built
locally by running ``python setup.py docs`` and to run the tests::

    pip install -r test-requirements.txt
    python setup.py test

The program can be installed and ran as follows::

    python setup.py install
    anti
