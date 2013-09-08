#!/usr/bin/python

import serial, sys

from usb_20 import *
from class_code import CLASS_CODE
from hid_11 import *
from langid import LANGID
from teensy_usb_proxy import *


# USB Device Class Definition for HID, Version 1.11
# Section B.1, Protocol 1 (Keyboard)
KEYBOARD_REPORT_DESCRIPTOR = ReportDescriptor(
          "\x05\x01"
        + "\x09\x06"
        + "\xA1\x01"
        + "\x75\x01"
        + "\x95\x08"
        + "\x05\x07"
        + "\x19\xE0"
        + "\x29\xE7"
        + "\x15\x00"
        + "\x25\x01"
        + "\x81\x02"
        + "\x95\x01"
        + "\x75\x08"
        + "\x81\x03"
        + "\x95\x05"
        + "\x75\x01"
        + "\x05\x08"
        + "\x19\x01"
        + "\x29\x05"
        + "\x91\x02"
        + "\x95\x01"
        + "\x75\x03"
        + "\x91\x03"
        + "\x95\x06"
        + "\x75\x08"
        + "\x15\x00"
        + "\x25\x68"
        + "\x05\x07"
        + "\x19\x00"
        + "\x29\x68"
        + "\x81\x00"
        + "\xc0"
        )

KEYBOARD_HID_DESCRIPTOR = Descriptor(
        descriptor_type = DESCRIPTOR_TYPE['HID']) / \
                HIDDescriptor(
                        num_descriptors = 1,
                        descriptors = [
                            DescriptorTypeLength(
                                descriptor_type = DESCRIPTOR_TYPE['Report'],
                                descriptor_length = len(KEYBOARD_REPORT_DESCRIPTOR),
                                ),])

DESCRIPTORS = {
        DESCRIPTOR_TYPE['CONFIGURATION'] : {
            0 : {
                0 : Descriptor(length = 9, descriptor_type = DESCRIPTOR_TYPE['CONFIGURATION']) / \
                        ConfigurationDescriptor(
                            num_interfaces = 1,
                            configuration_value = 1,
                            configuration = 0) / \
                        Descriptor(descriptor_type = DESCRIPTOR_TYPE['INTERFACE']) / \
                            InterfaceDescriptor(
                                num_endpoints = 1,
                                interface_class = CLASS_CODE['HID'],
                                interface_subclass = SUBCLASS_CODE['Boot'],
                                interface_protocol = PROTOCOL_CODE['Keyboard'],
                                ) / \
                        KEYBOARD_HID_DESCRIPTOR / \
                        Descriptor(descriptor_type = DESCRIPTOR_TYPE['ENDPOINT']) / \
                            EndpointDescriptor(
                                endpoint_direction = EndpointDescriptor.IN,
                                endpoint_number = 3,
                                transfer_type = EndpointDescriptor.INTERRUPT,
                                max_packet_size = 8,
                                interval = 1,
                                ),
                },
            },
        DESCRIPTOR_TYPE['DEVICE'] : {
            0 : {
                0 : Descriptor(descriptor_type = DESCRIPTOR_TYPE['DEVICE']) / \
                        DeviceDescriptor(
                            max_packet_size_0 = 32,
                            id_vendor = 0x26C0,
                            id_product = 0x247C,
                            device = 0x0100,
                            manufacturer = 1,
                            product = 2,
                            num_configurations = 1),
                },
            },
        DESCRIPTOR_TYPE['HID'] : {
            0 : {
                0 : KEYBOARD_HID_DESCRIPTOR,
                },
            },
        DESCRIPTOR_TYPE['Report'] : {
            0 : {
                0 : KEYBOARD_REPORT_DESCRIPTOR,
                },
            },
        DESCRIPTOR_TYPE['STRING'] : {
            0 : {
                0 : Descriptor(descriptor_type = DESCRIPTOR_TYPE['STRING']) / \
                        StringDescriptorZero()
                },
            1 : {
                LANGID['English (United States)'] : \
                        Descriptor(descriptor_type = DESCRIPTOR_TYPE['STRING']) / \
                        "TUP".encode('utf_16_le')
                },
            2 : {
                LANGID['English (United States)'] : \
                        Descriptor(descriptor_type = DESCRIPTOR_TYPE['STRING']) / \
                        "Proxy Keyboard".encode('utf_16_le')
                },
            },
        }

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout = None)

    u = TeensyUSBProxy(ser)
    u.init()
    u.enable()

    u.attach()

    while True:
        udint = ord(u.read('UDINT'))
        u.write('UDINT', 0)
        if udint & (1 << EORSTI):
            print '[*] found EORSTI'
            u.setupEndpoint(0, EP_TYPE_CONTROL, 32)

        ueint = ord(u.read('UEINTX'))
        if ueint & (1 << RXSTPI):
            print '[*] found RXSTPI'
            u.write('UENUM', 0)

            # read 8 byte setup packet
            p = u.readPacket(8)
            u.write('UEINTX', chr(~((1<<RXSTPI) | (1<<RXOUTI) | (1<<TXINI)) & 0xff))
            stp = Setup(p)
            print '[*] setup packet:'
            stp.show2()

            if stp.request == REQUEST_CODE['GET_CONFIGURATION']:
                print "[*] received GET_CONFIGURATION request"
                # wait for IN packet
                u.waitForInterrupt('UEINTX', 1 << TXINI)

                # send active configuration
                u.write('UEDATX', chr(u.configuration))

                # inform host about IN packet
                u.write('UEINTX', chr(~(1<<TXINI) & 0xff))

            elif stp.request == REQUEST_CODE['GET_DESCRIPTOR']:
                print "[*] received GET_DESCRIPTOR request"
                # wait for IN packet
                u.waitForInterrupt('UEINTX', 1 << TXINI)

                try:
                    desc = str(DESCRIPTORS[stp.descriptor_type][stp.descriptor_index][stp.index])
                    if len(desc) > stp.length:
                        print "[*] truncating descriptor"
                        desc = desc[0:stp.length]

                    # wait for IN packet
                    u.waitForInterrupt('UEINTX', 1 << TXINI)

                    # send desriptor
                    u.write('UEDATX', str(desc))

                    # inform host about IN packet
                    u.write('UEINTX', chr(~(1<<TXINI) & 0xff))
                except:
                    print "[-] Unknown descriptor, stalling"
                    u.write('UECONX', (1 << STALLRQ) | (1 << EPEN))

            elif stp.request == REQUEST_CODE['SET_ADDRESS']:
                print "[*] received SET_ADDRESS request"
                u.write('UEINTX', chr(~(1<<TXINI) & 0xff))
                u.waitForInterrupt('UEINTX', 1 << TXINI)
                u.write('UDADDR', stp.value | (1 << ADDEN))
