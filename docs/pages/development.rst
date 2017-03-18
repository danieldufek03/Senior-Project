===========
Development
===========

Currently the `pyshark <https://github.com/KimiNewt/pyshark>`_ library is being used to speed up prototyping and it has introduced the `tshark <https://www.wireshark.org/docs/man-pages/tshark.html>`_ dependency. ``pyshark`` is a wrapper for the ``tshark`` command line utility and makes use of its packet dissectors. This will likely change in the future.

Linux
-----

Setup a virtual environment to ensure system packages are not used::

    mkdir -p ~/.virtualenv/antikythera
    python3 -m venv ~/.virtualenv/antikythera
    source ~/.virtualenv/antikythera/bin/activate

Note that the command ``source ~/.virtualenv/antikythera/bin/activate`` must be reran for each new shell instance. When activated the name of the virtual environment should appear somewhere on the prompt such as:

    (antikythera) user@hostname:~$

Then for Debian or Ubuntu based distributions just run the setup script ``sudo bash setup.sh``. The documentation can be built locally by running ``python setup.py docs`` and to run the tests:

    pip install -r test-requirements.txt
    python setup.py test

The program can be installed and ran as follows:

    python setup.py install
    anti


Windows
-------

Wireshark must be installed for the ``pyshark`` library to have access to the packet dissectors it needs. See the [Wireshark Documentation](https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallWinInstall.html) for details.
