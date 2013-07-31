#!/usr/bin/python

import serial, sys

from usb_20 import *
from class_code import CLASS_CODE
from hid_11 import *
from langid import LANGID
from teensy_usb_proxy import *

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
                        Descriptor(descriptor_type = DESCRIPTOR_TYPE['HID']) / \
                            HIDDescriptor(
                                num_descriptors = 1,
                                descriptors = [
                                    DescriptorTypeLength(
                                        descriptor_type = DESCRIPTOR_TYPE['Report'],
                                        descriptor_length = 0,
                                        )
                                    ]
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

            if stp.request == REQUEST_CODE['GET_DESCRIPTOR']:
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
