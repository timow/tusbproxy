#!/usr/bin/python

# Definitions for USB class codes (Version 1.0)
# see http://www.usb.org/developers/defined_class

CLASS_CODE = {
        'Device'                         : 0x00,
        'Audio'                          : 0x01,
        'Communications and CDC Control' : 0x02,
        'HID'                            : 0x03,
        'Physical'                       : 0x05,
        'Image'                          : 0x06,
        'Printer'                        : 0x07,
        'Mass Storage'                   : 0x08,
        'Hub'                            : 0x09,
        'CDC-Data'                       : 0x0a,
        'Smart Card'                     : 0x0b,
        'Content Security'               : 0x0d,
        'Video'                          : 0x0e,
        'Personal Healthcare'            : 0x0f,
        'Audio/Video Device'             : 0x10,
        'Diagnostic Device'              : 0xdc,
        'Wireless Controller'            : 0xe0,
        'Miscellaneous'                  : 0xef,
        'Application Specific'           : 0xfe,
        'Vendor Specific'                : 0xff
        }
