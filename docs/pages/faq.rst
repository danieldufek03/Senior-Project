===
FAQ
===

Why Another IMSI-Catcher detector?
==================================

The problems with the existing solutions this project seeks to address are:

*   Technical knowledge and ability requirement
*   Only available for use on cellular telephones
*   Reliance on proprietary drivers

It is unreasonable to assume everyone that would want to and/or benefit from detecting IMSI-Catchers has the technical knowledge and ability to root their phone. Besides, rooting voids the warranty, has security risks, and must be repeated every new phone purchase. Needing to root every new phone can encourage security fatigue for someone who doesn't find that a fun way to spend their afternoon.

Phone apps are also completely unsuitable for use in an organizational setting, employees can't be expected to root their phones, install an app, and tell the IT security staff every time there is an alert. While antikythera will run on the small portable ARM tablet that has been developed, it can also run on, interface with, and take advantage of more powerful stationary hardware. On such a device it would provide centralized 24/7 security monitoring for malicious cellular activities that an organizations IT security staff could audit and monitor. In fact there are devices being sold, that are no different from the Finding Ray device, such as `DFRC's IMSI-Catcher Detector <http://www.dfrc.ch/imsi-catcher-detectors-for-global-safety/>`_ for 1-year Service at € 18000+ and a Stand Alone System for € 49000+. The Finding Ray device with a top-of-the-line URSP would cost less than $1000 to build.

.. epigraph::

    "You can't trust code that you did not totally create yourself. (Especially code from companies that employ people like me)."

    -- Ken Thompson

The last point is a matter of trust. Proprietary code, including drivers, can not be trusted and there are `many examples to prove it <https://www.gnu.org/proprietary/proprietary-back-doors.en.html>`_ examples of security through obscurity in proprietary code aside. Security is about people not technology, and people lie, cheat, and steal although usually for some motive be it personal gain or simply for demonstrating a system's vulnerability. Open source has the chance of being reviewed by many people who likely do not have the same motives and therefore a much greater change of being secure. Proprietary code has no place in secure devices.


Is it ready?
============

No, we are in early Alpha development and things are unstable and changing very quickly. There do exist solutions although their drawbacks that we are attempting to address apply. 

*   `SnoopSnitch <https://opensource.srlabs.de/projects/snoopsnitch>`_

    *   Currently the best established solution
    *   Many phones are not supported
    *   Must root the device
    *   Must have Qualcomm chipset and DIAG kernel driver
    *   Devices with custom ROM not supported

*   `Android IMSI-Catcher Detector (AIMSICD) <https://github.com/CellularPrivacy/Android-IMSI-Catcher-Detector>`_

    *   Currently in Alpha stage of development but much further along than antikythera
    *   Must root the device
    *   Supports more phones than SnoopSnitch
