tusbproxy -- Teensy USB Proxy
=============================

Tusbproxy implements a USB proxy for the [Teensy](http://www.pjrc.com/teensy/)
board allowing a (software) client to emulate an arbitrary USB device
(inspired by Travis Goodspeed's
[Facedancer](http://travisgoodspeed.blogspot.de/2012/07/emulating-usb-devices-with-python.html)
project).

Currently, only the Teensy++ 2.0 variant is supported. Feel free to contact me
if you would like to extend the implementation to other variants.

As illustrated below, the Teensy board running tusbproxy is connected to a USB
host via the Teensy's USB interface. The client is connected to the Teensy board
via a serial interface.

    +------------+         +----------+          +----------+
    |            |   USB   |          |  Serial  |          |
    |  USB Host  |---------|  Teensy  |----------|  Client  |
    |            |         |          |          |          |
    +------------+         +----------+          +----------+

The client can control the USB stack of the Teensy board via a dedicated
serial protocol. As such, the client can implement a USB device in software
(e.g., relying on scapy).


Requirements
------------

* Hardware:
  tusbproxy runs on a [Teensy++ 2.0 board](http://www.pjrc.com/teensy/) and
  requires the [UART serial port](http://www.pjrc.com/teensy/td_uart.html).

* Software:
  Compiling the Teensy proxy requires gcc-avr and make


Installation
------------

### Teensy Proxy

1. Compile the proxy:

       cd src/teensy/
       make


2. Deploy the resulting binary "tusbproxy.hex" using the
   [Teensy Loader](http://www.pjrc.com/teensy/loader.html).


Documentation
-------------

Needs to be improved ;-)

Refer to the [Atmel AT90USB1286
documentation](http://www.atmel.com/devices/at90usb1286.aspx) on how to control
the USB stack of the Teensy device.
