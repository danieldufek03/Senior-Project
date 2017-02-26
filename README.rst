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

Optionally just run the setup script ``setup.sh``.
For manual installation install Cython and Kivy dependancies::

    apt-get --yes update
    apt-get install deb-multimedia-keyring git build-essential
    apt-get install ffmpeg libsdl2-dev libsdl2-image-dev 
    apt-get install libswscale-dev libavformat-dev libavcodec-dev
    apt-get install zlib1g-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev

install tshark::

    apt-get --yes install tshark

Setup a virtual environment to ensure system packages are not used::

    mkdir -p ~/.virtualenv/antikythera
    python3 -m venv ~/.virtualenv/antikythera
    source ~/.virtualenv/antikythera/bin/activate

Install dependencies, because pip has no way to properly install the
dependencies in the correct order they are listed in the order which
they should be installed from top to bottom. The command below is a
workaround to this which automates the install::

    cat requirements.txt | xargs -n 1 -L 1 pip install
    pip install -r test-requirements.txt

Then the program can be installed and ran as follows::

    python setup.py install
    sonar [options]

Description
===========

Add details.
