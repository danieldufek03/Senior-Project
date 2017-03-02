#!/bin/bash
#
# Setup script for installing the Cython and 
# Kivy dependencies, and in the correct order.


# Assumes the python:latest image is used
debian_setup()
{

   	export DEBIAN_FRONTEND=noninteractive

    #Add repository for ffmpeg package
    echo "deb http://www.deb-multimedia.org jessie main non-free" >> /etc/apt/sources.list
    echo "deb-src http://www.deb-multimedia.org jessie main non-free" >> /etc/apt/sources.list

    # Install Kivy / Cython dependencies
    apt-get --yes update && apt-get --assume-yes --force-yes install deb-multimedia-keyring
    apt-get --yes update && apt-get --yes install git build-essential
    apt-get --yes install ffmpeg libsdl2-dev libsdl2-image-dev
    apt-get --yes install libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev
    apt-get --yes install libswscale-dev libavformat-dev libavcodec-dev
    apt-get --yes install zlib1g-dev
    apt-get --yes --assume-yes --force-yes install tshark
        
    # Install items in requirements.txt in order from top to bottom
    # This is required because the Cython package must be installed
    # before Kivy and pip provides no way to do this.
    pip install --upgrade pip
    cat requirements.txt | xargs -n 1 -L 1 pip install
    pip install -U setuptools

}


# Assumes the ubuntu:latest image is used
ubuntu_setup()
{

   	export DEBIAN_FRONTEND=noninteractive

    # Install Kivy / Cython dependencies
    apt-get --yes update && apt-get --yes install git build-essential
    apt-get --yes install ffmpeg libsdl2-dev libsdl2-image-dev
    apt-get --yes install libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev
    apt-get --yes install libswscale-dev libavformat-dev libavcodec-dev
    apt-get --yes install zlib1g-dev
    apt-get --yes install python3-dev
    apt-get --yes --assume-yes --force-yes install tshark
        
    # Install items in requirements.txt in order from top to bottom
    # This is required because the Cython package must be installed
    # before Kivy and pip provides no way to do this.
    pip install --upgrade pip
    cat requirements.txt | xargs -n 1 -L 1 pip install
    pip install -U setuptools

}


# Shell executer from a Debian environment
# All installation and configureation done server side.
shell_setup()
{

    # Install items in requirements.txt in order from top to bottom
    # This is required because the Cython package must be installed
    # before Kivy and pip provides no way to do this.
    pip install --upgrade pip
    cat requirements.txt | xargs -n 1 -L 1 pip3 install
    pip3 install -U setuptools

}


# Exit script if any statement returns non-true value
# Trace ERR through pipes
set -e
set -o pipefail

# Check for root
if (( $EUID != 0 )); then
    echo "[*] Please run with sudo or as root."
    exit 1
fi


ARCH="$(uname -m)" # Check if ARM or x86
OS="$(lsb_release -si)" # Check Linux Distribution
echo "[*] Detected system architecture $ARCH."
echo "[*] Detected Operating system $OS."


if [ $ARCH = "x86_64" ]; then

    if [ $OS = "debian" ]; then
        debian_setup
    elif [ $OS = "Ubuntu" ]; then
        ubuntu_setup
    else
        echo "[*] Operating system $OS not supported."
        echo "[*] Falling back to default setup."
        debian_setup
    fi

elif [ $ARCH = "armv7l" ]; then

    if [ -f /.dockerenv ]; then
        debian_setup
    else
        echo "[*] Installing without docker"
        shell_setup
    fi

else

    echo "[*] I do not know how to install the dependencies for this platform"
    exit 1

fi

echo "[*] Setup successful"
exit 0
