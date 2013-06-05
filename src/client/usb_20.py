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
