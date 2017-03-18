<h1 align="center">antikythera</h1>

<p align="center">
  <a target="_blank" href="https://gitlab.com/finding-ray/antikythera/pipelines"><img src="https://gitlab.com/finding-ray/antikythera/badges/master/build.svg"></a>
  <a target="_blank" href="https://finding-ray.gitlab.io/antikythera/htmlcov/index.html"><img src="https://gitlab.com/finding-ray/antikythera/badges/master/coverage.svg"></a>
  <a target="_blank" href="https://pypi.org/project/antikythera"><img src="https://img.shields.io/pypi/v/antikythera.svg"></a>
  <a target="_blank" href="https://www.gnu.org/licenses/gpl-3.0.en.html"><img src="https://img.shields.io/pypi/l/antikythera.svg"></a>
  <a target="_blank" href="#"><img src="https://img.shields.io/pypi/status/antikythera.svg"></a>
</p>

---

### IMSI-Catcher Detector

``antikythera`` is the software component of the IMSI-Catcher Detector device Finding Ray, although it is developed to work across many devices. It is built with Python to catch [IMSI-Catchers](https://en.wikipedia.org/wiki/IMSI-catcher), also known as Stingrays, Dirtboxes, or malicious base stations. IMSI-Catchers are used globally by many police departments to spy on citizens, organizations for corporate espionage, and other malicious actors seeking to Man-in-The-Middle (MiTM) cellular communications. Find more info in our [documentation on GitLab](http://finding-ray.gitlab.io/antikythera/).

Antikythera :

*  Designed to be usable on Windows, Linux, and OSX.
*  Capable of running on both x86 and ARM architectures (PCs, Android, iPhone, RaspberryPi, etc.)
*  Built to run without a lot of resources in an embedded environment.
*  Can use a software defined radio or hardware.

But most importantly it is not yet as advanced or reliable as [SnoopSnitch](https://opensource.srlabs.de/projects/snoopsnitch) and [AIMSICD](https://github.com/CellularPrivacy/Android-IMSI-Catcher-Detector). Both of which have also provided invaluable documentation allowing for this project to exist and attempt to provide an IMSI-Catcher detector that is not required to be a phone. And if you need real protection you should use one of them for now.


### Install

To install on Linux simply copy and paste this command into a shell:

    curl -sSL finding-ray.gitlab.io/install.sh | sh


### For Developers

See [the development documentation](http://finding-ray.gitlab.io/antikythera/) hosted on GitLab.
