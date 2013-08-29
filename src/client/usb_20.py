#!/usr/bin/python

from scapy.all import *

from class_code import CLASS_CODE
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
            ConditionalField(
                LEShortField('value', 0),
                lambda x: x.request != REQUEST_CODE['GET_DESCRIPTOR']),
            ConditionalField(
                ByteField('descriptor_index', 0),
                lambda x: x.request == REQUEST_CODE['GET_DESCRIPTOR']),
            ConditionalField(
                ByteEnumField('descriptor_type', DESCRIPTOR_TYPE['DEVICE'], DESCRIPTOR_TYPE),
                lambda x: x.request == REQUEST_CODE['GET_DESCRIPTOR']),
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
            # length field only covers the immediate descriptor, but not further payloads
            # (e.g., the basic config descriptor, but not further succeeding descriptors)
            l = (len(pkt) + len(self.payload) - len(self.payload.payload)) & 0xFF
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

# Table 9-10. Standard Configuration Descriptor 
class ConfigurationDescriptor(Packet):
    name = 'USB Standard Configuration Descriptor'

    fields_desc = [
            LEShortField('total_length', None),
            ByteField('num_interfaces', None),
            ByteField('configuration_value', 1),
            ByteField('configuration', 0),
            BitField('reserved_1', 1, 1),
            BitEnumField('self_powered', 1, 1, {'True': 1, 'False': 0}),
            BitEnumField('remote_wakeup', 1, 1, {'True': 1, 'False': 0}),
            BitField('reserved_0', 0, 5),
            ByteField('bMaxPower', 50),
            PacketListField('descriptors', None, Descriptor, length_from = lambda p: p.total_length - len(ConfigurationDescriptor()))
            ]

    # TODO: fix num_interfaces in post_build
    def post_build(self, pkt, pay):
        if self.total_length is None and pay:
            l = (2 + len(pkt) + len(pay)) & 0xFFFF
            pkt = struct.pack('<H', l) + pkt[2:]
        return pkt + pay
bind_layers(Descriptor, ConfigurationDescriptor, descriptor_type = DESCRIPTOR_TYPE['CONFIGURATION'])

# Table 9-12. Standard Interface Descriptor 
class InterfaceDescriptor(Packet):
    name = 'USB Standard Interface Descriptor'

    fields_desc = [
            ByteField('interface_number', 0),
            ByteField('alternate_setting', 0),
            ByteField('num_endpoints', 0),
            ByteEnumField('interface_class', CLASS_CODE['Device'], CLASS_CODE),
            ByteField('interface_subclass', 0),
            ByteField('interface_protocol', 0),
            ByteField('interface', 0),
            ]
bind_layers(Descriptor, InterfaceDescriptor, descriptor_type = DESCRIPTOR_TYPE['INTERFACE'])
bind_layers(InterfaceDescriptor, Descriptor)

# Table 9-13. Standard Endpoint Descriptor 
class EndpointDescriptor(Packet):
    name = 'USB Standard Endpoint Descriptor'

    # endpoint direction
    OUT = 0
    IN  = 1

    # usage type
    DATA              = 0
    FEEDBACK          = 1
    IMPLICIT_FEEDBACK = 2
    RESERVED          = 3

    # synchronization type
    NO_SYNC  = 0
    ASYNC    = 1
    ADAPTIVE = 2
    SYNC     = 3

    # transfer type
    CONTROL     = 0
    ISOCHRONOUS = 1
    BULK        = 2
    INTERRUPT   = 3

    fields_desc = [
            BitEnumField('endpoint_direction', 0, 1, {OUT : 'OUT', IN : 'IN'}),
            BitField('reserved_0', 0, 3),
            BitField('endpoint_number', 0, 4),
            BitField('reserved_1', 0, 2),

            # TODO: undefined for isochronous endpoints...
            BitEnumField('usage_type', 0, 2, {
                DATA              : 'Data',
                FEEDBACK          : 'Feedback',
                IMPLICIT_FEEDBACK : 'Implicit Feedback Data',
                RESERVED          : 'Reserved'}),

            # TODO: undefined for isochronous endpoints...
            BitEnumField('sync_type', 0, 2, {
                NO_SYNC  : 'No Synchronization',
                ASYNC    : 'Asynchronous',
                ADAPTIVE : 'Adaptive',
                SYNC     : 'Synchronous'}),

            BitEnumField('transfer_type', 0, 2, {
                CONTROL     : 'Control',
                ISOCHRONOUS : 'Isochronous',
                BULK        : 'Bulk',
                INTERRUPT   : 'Interrupt'}),

            # TODO: more complex for isochronous endpoints...
            LEShortField('max_packet_size', 0),

            ByteField('interval', 0),
            ]
bind_layers(Descriptor, EndpointDescriptor, descriptor_type = DESCRIPTOR_TYPE['ENDPOINT'])

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

# Table 9-16. UNICODE String Descriptor
class StringDescriptor(Packet):
    name = 'USB String Descriptor'
    
    fields_desc = [
            # TODO: reflect the UTF16 encoding
            StrLenField('string', '',
                length_from = lambda pkt: pkt.underlayer.length - 2
                    if pkt.underlayer else len(pkt)),
            ]
bind_layers(Descriptor, StringDescriptor, descriptor_type = DESCRIPTOR_TYPE['STRING'])
