#!/usr/bin/python

from scapy.all import *

from usb_20 import *

class ItemEnumField(StrFixedLenField):
    def __init__(self, name, default, length=None, enum=None, length_from=None):
        StrFixedLenField.__init__(self, name, default, length=length, length_from=length_from)
        self.enum = enum
    def i2repr(self, pkt, v):
        r = v.lstrip("\0")
        if v in self.enum:
            return "%s (%s)" % (repr(v), self.enum[v])
        elif r in self.enum:
            return "%s (%s)" % (repr(v), self.enum[r])

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

# Section 6.2.2.4 Main Items
MAIN_ITEM_TAG = {
        'Input'          : 0b1000,
        'Output'         : 0b1001,
        'Feature'        : 0b1011,
        'Collection'     : 0b1010,
        'End Collection' : 0b1100,
        }

# Section 6.2.2.7 Global Items
GLOBAL_ITEM_TAG = {
        'Usage Page'       : 0b0000,
        'Logical Minimum'  : 0b0001,
        'Logical Maximum'  : 0b0010,
        'Physical Minimum' : 0b0011,
        'Physical Maximum' : 0b0100,
        'Unit Exponent'    : 0b0101,
        'Unit'             : 0b0110,
        'Report Size'      : 0b0111,
        'Report ID'        : 0b1000,
        'Report Count'     : 0b1001,
        'Push'             : 0b1010,
        'Pop'              : 0b1011,
        }

# Section 6.2.2.8 Local Items
LOCAL_ITEM_TAG = {
        'Usage'              : 0b0000,
        'Usage Minimum'      : 0b0001,
        'Usage Maximum'      : 0b0010,
        'Designator Index'   : 0b0011,
        'Designator Minimum' : 0b0100,
        'Designator Maximum' : 0b0101,
        'String Index'       : 0b0111,
        'String Minimum'     : 0b1000,
        'String Maximum'     : 0b1001,
        'Delimiter'          : 0b1010,
        }

# Section 6.2.2.2 Short Items
ITEM_TYPE = {
        'Main'     : 0,
        'Global'   : 1,
        'Local'    : 2,
        'Reserved' : 3
        }
ITEM_SIZE = {
        '0' : 0,
        '1' : 1,
        '2' : 2,
        '4' : 3
        }
class ShortItem(Packet):
    name = 'USB HID Short Item'
    
    fields_desc = [
            MyBitMultiEnumField('tag', 0, 4, {
                ITEM_TYPE['Main']     : MAIN_ITEM_TAG,
                ITEM_TYPE['Global']   : GLOBAL_ITEM_TAG,
                ITEM_TYPE['Local']    : LOCAL_ITEM_TAG,
                ITEM_TYPE['Reserved'] : {},
                },
                depends_on = lambda pkt: pkt.item_type),
            BitEnumField('item_type', ITEM_TYPE['Main'], 2, ITEM_TYPE),
            BitEnumField('size', ITEM_SIZE['0'], 2, ITEM_SIZE),
            ]

    def extract_padding(self, s):
        # hard-coded reverse mapping of ITEM_SIZE
        item_size = self.size if self.size != 3 else 4
        return s[:item_size], s[item_size:]


# Section 6.2.2.6, Collection
class Collection(Packet):
    name = 'USB HID Collection'

    PHYSICAL       = '\x00'
    APPLICATION    = '\x01'
    LOGICAL        = '\x02'
    REPORT         = '\x03'
    NAMED_ARRAY    = '\x04'
    USAGE_SWITCH   = '\x05'
    USAGE_MODIFIER = '\x06'

    fields_desc = [
            ItemEnumField('collection_type', PHYSICAL, enum = {
                PHYSICAL       : 'Physical',
                APPLICATION    : 'Application',
                LOGICAL        : 'Logical',
                REPORT         : 'Report',
                NAMED_ARRAY    : 'Named Array',
                USAGE_SWITCH   : 'Usage Switch',
                USAGE_MODIFIER : 'Usage Modifier',},
                length_from = lambda pkt: pkt.underlayer.size)
            ]
bind_layers(ShortItem, Collection, item_type = ITEM_TYPE['Main'], tag = MAIN_ITEM_TAG['Collection'])


# USB HID Usage Tables, Table 1, Usage Page Summary
class UsagePage(Packet):
    name = 'USB HID Usage Page'

    UNDEFINED                       = '\x00'
    GENERIC_DESKTOP_CONTROLS        = '\x01'
    SIMULATION_CONTROLS             = '\x02'
    VR_CONTROLS                     = '\x03'
    SPORT_CONTROLS                  = '\x04'
    GAME_CONTROLS                   = '\x05'
    GENERIC_DEVICE_CONTROLS         = '\x06'
    KEYBOARD_KEYPAD                 = '\x07'
    LEDS                            = '\x08'
    BUTTON                          = '\x09'
    ORDINAL                         = '\x0A'
    TELEPHONY                       = '\x0B'
    CONSUMER                        = '\x0C'
    DIGITIZER                       = '\x0D'
    PID_PAGE                        = '\x0F'
    UNICODE                         = '\x10'
    ALPHANUMERIC_DISPLAY            = '\x14'
    MEDICAL_INSTRUMENTS             = '\x40'
    MONITOR_PAGES_80                = '\x80'
    MONITOR_PAGES_81                = '\x81'
    MONITOR_PAGES_82                = '\x82'
    MONITOR_PAGES_83                = '\x83'
    POWER_PAGES_84                  = '\x84'
    POWER_PAGES_85                  = '\x85'
    POWER_PAGES_86                  = '\x86'
    POWER_PAGES_87                  = '\x87'
    BAR_CODE_SCANNER_PAGE           = '\x8C'
    SCALE_PAGE                      = '\x8D'
    MAGNETIC_STRIPE_READING_DEVICES = '\x8E'
    RESERVED_POINT_OF_SALE_PAGES    = '\x8F'
    CAMERA_CONTROL_PAGE             = '\x90'
    ARCADE_PAGE                     = '\x91'

    fields_desc = [
            ItemEnumField('usage_page', UNDEFINED, enum = {
                UNDEFINED                       : 'Undefined',
                GENERIC_DESKTOP_CONTROLS        : 'Generic Desktop Controls',
                SIMULATION_CONTROLS             : 'Simulation Controls',
                VR_CONTROLS                     : 'VR Controls',
                SPORT_CONTROLS                  : 'Sport Controls',
                GAME_CONTROLS                   : 'Game Controls',
                GENERIC_DEVICE_CONTROLS         : 'Generic Device Controls',
                KEYBOARD_KEYPAD                 : 'Keyboard/Keypad',
                LEDS                            : 'LEDs',
                BUTTON                          : 'Button',
                ORDINAL                         : 'Ordinal',
                TELEPHONY                       : 'Telephony',
                CONSUMER                        : 'Consumer',
                DIGITIZER                       : 'Digitizer',
                PID_PAGE                        : 'PID Page',
                UNICODE                         : 'Unicode',
                ALPHANUMERIC_DISPLAY            : 'Alphanumeric Display',
                MEDICAL_INSTRUMENTS             : 'Medical Instruments',
                MONITOR_PAGES_80                : 'Monitor Pages 80',
                MONITOR_PAGES_81                : 'Monitor Pages 81',
                MONITOR_PAGES_82                : 'Monitor Pages 82',
                MONITOR_PAGES_83                : 'Monitor Pages 83',
                POWER_PAGES_84                  : 'Power Pages 84',
                POWER_PAGES_85                  : 'Power Pages 85',
                POWER_PAGES_86                  : 'Power Pages 86',
                POWER_PAGES_87                  : 'Power Pages 87',
                BAR_CODE_SCANNER_PAGE           : 'Bar Code Scanner Page',
                SCALE_PAGE                      : 'Scale Page',
                MAGNETIC_STRIPE_READING_DEVICES : 'Magnetic Stripe Reading Devices',
                RESERVED_POINT_OF_SALE_PAGES    : 'Reserved Point of Sale Pages',
                CAMERA_CONTROL_PAGE             : 'Camera Control Page',
                ARCADE_PAGE                     : 'Arcade Page',},
                length_from = lambda pkt: pkt.underlayer.size)
            ]
bind_layers(ShortItem, UsagePage, item_type = ITEM_TYPE['Global'], tag = GLOBAL_ITEM_TAG['Usage Page'])

class ReportDescriptor(Packet):
    name = 'USB HID Report Descriptor'
    fields_desc = [
            PacketListField("items", [], ShortItem)
            ]

class HIDDescriptor(Packet):
    name = 'USB HID Descriptor'
    
    fields_desc = [
            XLEShortField('hid', 0x0111),
            ByteEnumField('country_code', COUNTRY_CODE['Not Supported'], COUNTRY_CODE),
            ByteField('num_descriptors', None), # TODO:counter for descriptor type / length
            PacketListField('descriptors', [], DescriptorTypeLength,
                count_from = lambda p: p.num_descriptors)
            ]
    def extract_padding(self, s):
        return None, s
bind_layers(Descriptor, HIDDescriptor, descriptor_type = DESCRIPTOR_TYPE['HID'])
