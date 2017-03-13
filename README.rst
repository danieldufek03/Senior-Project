===========
antikythera
===========

.. image:: https://gitlab.com/finding-ray/antikythera/badges/master/build.svg
    :target: https://gitlab.com/finding-ray/antikythera/pipelines
.. image:: https://gitlab.com/finding-ray/antikythera/badges/master/coverage.svg
    :target: https://finding-ray.gitlab.io/antikythera/htmlcov/index.html

IMSI Catcher detection, analysis and display.

Development Environment Setup
=============================

Windows
-------

Wireshark must be installed for the ``pyshark`` library to have
access to the packet dissectors it needs. See the 
`Wireshark Documentation <https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallWinInstall.html>`_
for details.

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