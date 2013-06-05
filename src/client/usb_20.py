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
