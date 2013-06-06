#!/usr/bin/python

from scapy.all import *
from langid import LANGID

class XLEShortField(LEShortField):
    def i2repr(self, pkt, x):
        return lhex(self.i2h(pkt, x))
scapy.fields.XLEShortField = XLEShortField

# Table 9-4. Standard Request Codes
REQUEST_CODE = {
        'GET_STATUS'        : 0,
        'CLEAR_FEATURE'     : 1,
        'SET_FEATURE'       : 3,
        'SET_ADDRESS'       : 5, 
        'GET_DESCRIPTOR'    : 6,
        'SET_DESCRIPTOR'    : 7,
        'GET_CONFIGURATION' : 8,
        'SET_CONFIGURATION' : 9,
        'GET_INTERFACE'     : 10,
        'SET_INTERFACE'     : 11,
        'SYNCH_FRAME'       : 12,
        }

# Table 9-5. Descriptor Types
DESCRIPTOR_TYPE = {
        'DEVICE'                            : 1,
        'CONFIGURATION'                     : 2,
        'STRING'                            : 3,
        'INTERFACE'                         : 4,
        'ENDPOINT'                          : 5,
        'DEVICE_QUALIFIER'                  : 6,
        'OTHER_SPEED_CONFIGURATION'         : 7,
        'INTERFACE_POWER'                   : 8
        }

# Section 9.3. Setup Data
class Setup(Packet):
    name = 'USB Setup Packet'

    DIR_HOST_TO_DEVICE = 0
    DIR_DEVICE_TO_HOST = 1

    TYPE_STANDARD = 0
    TYPE_CLASS    = 1
    TYPE_VENDOR   = 2
    TYPE_RESERVED = 3
    
    RCPT_DEVICE      = 0
    RCPT_INTERFACE   = 1
    RCPT_ENDPOINT    = 2
    RCPT_OTHER       = 3


    fields_desc = [
            BitEnumField('data_xfer_direction', 0, 1, {
                DIR_HOST_TO_DEVICE : 'Host-to-device',
                DIR_DEVICE_TO_HOST : 'Device-to-host'}),
            BitEnumField('type', 0, 2, {
                TYPE_STANDARD : 'Standard',
                TYPE_CLASS    : 'Class',
                TYPE_VENDOR   : 'Vendor',
                TYPE_RESERVED : 'Reserved'}),
            BitEnumField('recipient', 0, 5, {
                RCPT_DEVICE    : 'Device',
                RCPT_INTERFACE : 'Interface',
                RCPT_ENDPOINT  : 'Endpoint',
                RCPT_OTHER     : 'Other'}),
            ByteEnumField('request', 0, REQUEST_CODE),
            LEShortField('value', 0),
            LEShortField('index', 0),
            LEShortField('length', 0),
            ]

class Descriptor(Packet):
    name = 'USB Standard Descriptor'

    fields_desc = [
            ByteField('length', None),
            ByteEnumField('descriptor_type', DESCRIPTOR_TYPE['DEVICE'], DESCRIPTOR_TYPE),
            ]

    def post_build(self, pkt, pay):
        if self.length is None and pay:
            l = (len(pkt) + len(pay)) & 0xFF
            pkt = chr(l) + pkt[1:]
        return pkt + pay


# Table 9-8. Standard Device Descriptor 
class DeviceDescriptor(Packet):
    name = 'USB Standard Device Descriptor'

    fields_desc = [
            XLEShortField('usb', 0x0200),
            XByteField('device_class', 0),
            XByteField('device_subclass', 0),
            XByteField('device_protocol', 0),
            ByteField('max_packet_size_0', 64),
            XLEShortField('id_vendor', 0),
            XLEShortField('id_product', 0),
            XLEShortField('device', 0),
            ByteField('manufacturer', 0),
            ByteField('product', 0),
            ByteField('serial_number', 0),
            ByteField('num_configurations', 0),
    ]
bind_layers(Descriptor, DeviceDescriptor, descriptor_type = DESCRIPTOR_TYPE['DEVICE'])

# Table 9-15. String Descriptor Zero
class StringDescriptorZero(Packet):
    name = 'USB String Descriptor Zero'

    fields_desc = [
            FieldListField('LANGIDs',
                [LANGID['English (United States)']],
                LEShortEnumField('LANGID', LANGID['English (United States)'],
                    LANGID),
                count_from = lambda pkt: pkt[StringDescriptorZero].get_lang_id_count()),
            ]
    
    def get_lang_id_count(self):
        descriptor = self.underlayer
        
        if descriptor:
            # omit 2 bytes for descriptor header
            # consider 2 bytes per lang id
            n_lang_ids = (descriptor.length - 2) / 2
        else:
            n_lang_ids = len(self.LANGIDs) / 2

        return nr_lang_ids
bind_layers(Descriptor, StringDescriptorZero, descriptor_type = DESCRIPTOR_TYPE['STRING'])
