#!/usr/bin/python

from scapy.all import *

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
