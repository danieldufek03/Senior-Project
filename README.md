<h2 align="center">antikythera</h2>

<p align="center">
  <a target="_blank" href="https://gitlab.com/finding-ray/antikythera/pipelines"><img src="https://gitlab.com/finding-ray/antikythera/badges/master/build.svg"></a>
  <a target="_blank" href="https://finding-ray.gitlab.io/antikythera/htmlcov/index.html"><img src="https://gitlab.com/finding-ray/antikythera/badges/master/coverage.svg"></a>
  <a target="_blank" href="https://pypi.org/project/antikythera"><img src="https://img.shields.io/pypi/v/antikythera.svg"></a>
  <a target="_blank" href="https://www.gnu.org/licenses/gpl-3.0.en.html"><img src="https://img.shields.io/pypi/l/antikythera.svg"></a>
  <a target="_blank" href="#"><img src="https://img.shields.io/pypi/status/antikythera.svg"></a>
</p>

---

### IMSI-Catcher Detector

``antikythera`` is the software component of the IMSI-Catcher Detector device Finding Ray, although it is developed to work across many devices. It is built with Python to catch [IMSI-Catchers](https://en.wikipedia.org/wiki/IMSI-catcher), also known as Stingrays, Dirtboxes, or malicious base stations. IMSI-Catchers are used globally by many police departments to spy on citizens, organizations for corporate espionage, and other malicious actors seeking to Man-in-The-Middle (MiTM) cellular communications. For more info see the [documentation on GitLab](http://finding-ray.gitlab.io/antikythera/).

&nbsp;
### Warning

antikythera is not yet as advanced or reliable as [SnoopSnitch](https://opensource.srlabs.de/projects/snoopsnitch) and [AIMSICD](https://github.com/CellularPrivacy/Android-IMSI-Catcher-Detector). Both of which have also provided invaluable documentation allowing for this project to exist and attempt to provide an IMSI-Catcher detector that is not required to be a phone. And if you need real protection you should use one of them for now, preferably SnoopSnitch as it is the best tested currently. For a detailed description of the other options see the FAQ:

*   [Is it ready?](http://finding-ray.gitlab.io/antikythera/faq.html#is-it-ready)
*   [Why another IMSI-Catcher Detector?](http://finding-ray.gitlab.io/antikythera/faq.html#why-another-imsi-catcher-detector)

&nbsp;
### Install


To install on Linux simply copy and paste this command into a shell:

    curl -sSL finding-ray.gitlab.io/install.sh | sh

&nbsp;
### Usage

Although antikythera is designed to run on Windows, Linux, and OSX currently automated install is only available for Debian based Linux distributions. It will run on both x86 and ARM architectures (PCs, Android, iPhone, RaspberryPi, etc.) and is built to work well without a lot of resources in an embedded environment. It is possible to read data from a capture ([pcap file](https://en.wikipedia.org/wiki/Pcap)) file but it requires an interface to a radio for live capture and both a software defined radio or hardware radio can be used, but it must provide data in the [GSMTAP](http://osmocom.org/projects/baseband/wiki/GSMTAP) format. For more info on the radio requirements see the [hardware documentation](http://finding-ray.gitlab.io/antikythera/hardware.html).

&nbsp;
Kivy arguments come first then antikythera's with ``--`` separating them:

    anti [kivy options] -- [antikythera options]

&nbsp;
Provide ``-h`` on either side to see the options available. Kivy will start spinning up as soon as it is imported so if you ask for the antikythera help there will be some output before it is displayed and exits.

    anti -h         # display kivy options for the display
    anti -- -h      # display antikythera options the program

&nbsp;
Run with very-verbose logging, a queue size of 1000 for incoming packets, and use a capture file for input:

    anti -- -vv -q 1000 -c tests/test_data/intercepting_catcher.pcap

&nbsp;
### For Developers

See [the development documentation](http://finding-ray.gitlab.io/antikythera/pages/development.html) hosted on GitLab for information on setting up a development environment.
