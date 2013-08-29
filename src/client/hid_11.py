#!/usr/bin/python

from scapy.all import *

from usb_20 import *

# USB Device Class Definition for HID, Version 1.11

# Section 7.1. Standard Requests
DESCRIPTOR_TYPE.update({
        'HID'                 : 0x21,
        'Report'              : 0x22,
        'Physical Descriptor' : 0x23,
        })

# Section 4.2. Subclass Codes
SUBCLASS_CODE = {
        'No Subclass' : 0x00,
        'Boot'        : 0x01,
        }

# Section 4.3. Protocol Codes
PROTOCOL_CODE = {
        'None'     : 0x00,
        'Keyboard' : 0x01,
        'Mouse'    : 0x02,
        }

# Section 6.2.1. Country Code
COUNTRY_CODE = {
        'Not Supported'       : 0,
        'Arabic'              : 1,
        'Belgian'             : 2,
        'Canadian-Bilingual'  : 3,
        'Canadian-French'     : 4,
        'Czech Republic'      : 5,
        'Danish'              : 6,
        'Finnish'             : 7,
        'French'              : 8,
        'German'              : 9,
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

# Section 6.2.1 HID Descriptor
class DescriptorTypeLength(Packet):
    name = 'USB HID Descriptor Type / Length'

    fields_desc = [
            ByteEnumField('descriptor_type', DESCRIPTOR_TYPE['DEVICE'], DESCRIPTOR_TYPE),
            LEShortField('descriptor_length', 0)
            ]

    def extract_padding(self, s):
        return (None, s)

class HIDDescriptor(Packet):
    name = 'USB HID Descriptor'
    
    fields_desc = [
            XLEShortField('hid', 0x0111),
            ByteEnumField('country_code', COUNTRY_CODE['Not Supported'], COUNTRY_CODE),
            ByteField('num_descriptors', None), # TODO:counter for descriptor type / length
            PacketListField('descriptors', [], DescriptorTypeLength,
                count_from = lambda p: p.num_descriptors)
            ]
bind_layers(Descriptor, HIDDescriptor, descriptor_type = DESCRIPTOR_TYPE['HID'])
bind_layers(HIDDescriptor, Descriptor)

