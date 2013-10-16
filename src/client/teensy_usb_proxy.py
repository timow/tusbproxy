#!/usr/bin/python

CMD_READ  = 0b00000000
CMD_WRITE = 0b10000000

TYPE_IO8  = 0b00000000
TYPE_MEM8 = 0b01000000

SMALL_N   = 0b00100000

REG = {
        'PLLCSR'  : (TYPE_IO8,  chr(0x29)),
        'PORTD'   : (TYPE_IO8,  chr(0x0b)),
        'UDCON'   : (TYPE_MEM8, chr(0xe0)),
        'UDINT'   : (TYPE_MEM8, chr(0xe1)),
        'UDADDR'  : (TYPE_MEM8, chr(0xe3)),
        'UECFG0X' : (TYPE_MEM8, chr(0xec)),
        'UECFG1X' : (TYPE_MEM8, chr(0xed)),
        'UECONX'  : (TYPE_MEM8, chr(0xeb)),
        'UEDATX'  : (TYPE_MEM8, chr(0xf1)),
        'UEINTX'  : (TYPE_MEM8, chr(0xe8)),
        'UENUM'   : (TYPE_MEM8, chr(0xe9)),
        'UERST'   : (TYPE_MEM8, chr(0xea)),
        'UHWCON'  : (TYPE_MEM8, chr(0xd7)),
        'USBCON'  : (TYPE_MEM8, chr(0xd8)),
        }

# PLLCSR
PLLP2   = 4
PLLP1   = 3
PLLP0   = 2
PLLE    = 1
PLOCK   = 0

# UDCON
LSM     = 2
RMWKUP  = 1
DETACH  = 0

# UDINT
UPRSMI  = 6
EORSMI  = 5
WAKEUPI = 4
EORSTI  = 3
SOFI    = 2
SUSPI   = 0

# UDADDR
ADDEN   = 7

# UECFG0X
EPTYPE1 = 7
EPTYPE0 = 6
EPDIR   = 0

# UECFG1X
EPSIZE2 = 6
EPSIZE1 = 5
EPSIZE0 = 4
EPBK1   = 3
EPBK0   = 2
ALLOC   = 1

# UECONX
STALLRQ  = 5
STALLRQC = 4
RSTDT    = 3
EPEN     = 0

# UEINTX
FIFOCON  = 7
NAKINI   = 6
RWAL     = 5
NAKOUTI  = 4
RXSTPI   = 3
RXOUTI   = 2
STALLEDI = 1
TXINI    = 0

# UHWCON
UIMOD  = 7
UIDE   = 6
UVCONE = 4
UVREGE = 0

# USBCON
USBE    = 7
HOST    = 6
FRZCLK  = 5
OTGPADE = 4
IDTE    = 1
VBUSTE  = 0

EP_TYPE_CONTROL     = 0b00000000
EP_TYPE_ISOCHRONOUS = 0b01000000
EP_TYPE_BULK        = 0b10000000
EP_TYPE_INTERRUPT   = 0b11000000

EP_SIZE = {
        8   : 0b00000000,
        16  : 0b00010000,
        32  : 0b00100000,
        64  : 0b00110000,
        128 : 0b01000000,
        256 : 0b01010000,
        }

# TODO: separate proxy-specific parts from USB device-specific parts
class TeensyUSBProxy:
    def __init__(self, ser):
        self.ser = ser
        self.configuration = None

    def read(self, reg, n = 1):
        t,o = REG[reg]
        if n < 32:
            self.ser.write(chr(CMD_READ | t | SMALL_N | n) + o)
        else:
            self.ser.write(chr(CMD_READ | t | (n >> 8)) + (n % 256) + o)
        return self.ser.read(n)

    def write(self, reg, vals):
        t,o = REG[reg]

        if type(vals) == int:
            vals = chr(vals)

        n = len(vals)

        if n < 32:
            self.ser.write(chr(CMD_WRITE | t | SMALL_N | n) + o + vals)
        else:
            self.ser.write(chr(CMD_WRITE | t | (n >> 8)) + (n % 256) + o + vals)

    def waitForInterrupt(self, reg, intrMask):
        intr = ord(self.read(reg))
        while (intr & intrMask) == 0:
            intr = ord(self.read(reg))

        return intr

    def led_on(self):
        self.write('PORTD', ord(self.read('PORTD')) | (1 << 6))

    def led_off(self):
        self.write('PORTD', ord(self.read('PORTD')) & ~(1 << 6))


    def init(self):
        # enable device mode and USB pad
        self.write('UHWCON', (1 << UIMOD) | (1 << UVREGE))

        # enable USB, but freeze clock for now
        self.write('USBCON', (1 << USBE) | (1 << FRZCLK))

        # enable PLL and configure PLL input prescale
        self.write('PLLCSR', (1 << PLLP2) | (1 << PLLP0) | (1 << PLLE))

        # wait for PLL to be locked to the reference clock
        while (ord(self.read('PLLCSR')) & (1 << PLOCK)) == 0:
            continue

    def readPacket(self, l):
        return self.read('UEDATX', l)

    def enable(self):
        # enable USB controller and OTG/VBUS pad,
        # unfreeze clock
        self.write('USBCON', (1 << USBE) | (1 << OTGPADE))

    def disable(self):
        # disable USB controller and OTG/VBUS pad
        self.write('USBCON', 0x00)

    def attach(self):
        self.write('UDCON', 0x00)

    def detach(self):
        self.write('UDCON', 1 << DETACH)
        self.led_off()

    def setupEndpoint(self, nr, epType, size):
        # select EP
        self.write('UENUM', nr)

        # enable EP
        self.write('UECONX', 1 << EPEN)

        # set EP type
        self.write('UECFG0X', epType)

        # set EP size (and single buffer)
        self.write('UECFG1X', EP_SIZE[size] | 0x02)
