#!/usr/bin/python

from scapy.all import *

# USB Device Class Definition for HID, Version 1.11

COUNTRY_CODE = {
        'Not Supported'       : 00,
        'Arabic'              : 01,
        'Belgian'             : 02,
        'Canadian-Bilingual'  : 03,
        'Canadian-French'     : 04,
        'Czech Republic'      : 05,
        'Danish'              : 06,
        'Finnish'             : 07,
        'French'              : 08,
        'German'              : 09,
        'Greek'               : 10,
        'Hebrew'              : 11,
        'Hungary'             : 12,
        'International (ISO)' : 13,
        'Italian'             : 14,
        'Japan (Katakana)'    : 15,
        'Korean'              : 16,
        'Latin American'      : 17,
        'Netherlands/Dutch'   : 18,
        'Norwegian'           : 19,
        'Persian (Farsi)'     : 20,
        'Poland'              : 21,
        'Portuguese'          : 22,
        'Russia'              : 23,
        'Slovakia'            : 24,
        'Spanish'             : 25,
        'Swedish'             : 26,
        'Swiss/French'        : 27,
        'Swiss/German'        : 28,
        'Switzerland'         : 29,
        'Taiwan'              : 30,
        'Turkish-Q'           : 31,
        'UK'                  : 32,
        'US'                  : 33,
        'Yugoslavia'          : 34,
        'Turkish-F'           : 35,
        }

class DescriptorTypeLength(Packet):
    name = 'USB HID Descriptor Type / Length'

    fields_desc = [
            ByteField('descriptor_type', 0),
            LEShortField('descriptor_length', 0)
            ]


# Section 6.2.1 HID Descriptor
class HIDDescriptor(Packet):
    name = 'USB HID Descriptor'
    
    fields_desc = [
            XLEShortField('hid', 0x010b),
            ByteEnumField('country_code', COUNTRY_CODE['US'], COUNTRY_CODE),
            ByteField('num_descriptors', 1), # TODO:counter for descriptor type / length
            ByteField('descriptor_type', 0),
            LEShortField('descriptor_length', 0), # TODO: descriptor_packets
            PacketListField('descriptors', None, DescriptorTypeLength,
                count_from = lambda p: p.num_descriptors)
            ]
