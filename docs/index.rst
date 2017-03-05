===========
antikythera
===========

.. image:: https://gitlab.com/finding-ray/antikythera/badges/master/build.svg
    :target: https://gitlab.com/finding-ray/antikythera/pipelines
.. image:: https://gitlab.com/finding-ray/antikythera/badges/master/coverage.svg
    :target: https://finding-ray.gitlab.io/antikythera/htmlcov/index.html

This is the documentation of **antikythera**, the portable 
:abbr:`IMSI (International Mobile Subscribers Identity)` catcher detector
`gitlab.com/finding-ray/antikythera <https://gitlab.com/finding-ray/antikythera>`_.

:abbr:`GUI (Graphical User Interface)` dependancies Debian::

    sudo apt-get update -y && sudo apt-get install -y \
        python-pip \
        build-essential \
        git \
        python \
        python-dev \
        ffmpeg \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
        libportmidi-dev \
        libswscale-dev \
        libavformat-dev \
        libavcodec-dev \
        zlib1g-dev

:abbr:`GUI (Graphical User Interface)` dependancies ARM::

    sudo apt-get update
    sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       pkg-config libgl1-mesa-dev libgles2-mesa-dev \
       python-setuptools libgstreamer1.0-dev git-core \
       gstreamer1.0-plugins-{bad,base,good,ugly} \
       gstreamer1.0-{omx,alsa} python-dev cython


Quick development setup::

    apt-get install python3
    mkdir -p ~/.virtualenv
    python3 -m venv ~/.virtualenv/antikythera
    source ~/.virtualenv/antikythera/bin/activate
    cat requirements.txt | xargs -n 1 -L 1 pip install
    pip install -r test-requirements.txt
    pip install -U setuptools

Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Changelog <changes>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
