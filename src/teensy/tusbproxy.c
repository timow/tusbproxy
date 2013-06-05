/* 
 * tusbproxy -- Teensy USB proxy
 */

#include <avr/pgmspace.h>

#include "uart.h"

#define LED_CONFIG	(DDRD |= (1<<6))
#define CPU_PRESCALE(n)	(CLKPR = 0x80, CLKPR = (n))

#define CMD_READ_IO8     0x00
#define CMD_READ_MEM8    0x40
#define CMD_WRITE_IO8    0x80
#define CMD_WRITE_MEM8   0xC0
#define CMD_MASK         0xC0

#define SMALL_COUNT_MASK 0x20
#define COUNT_MASK       0x1F

int main(void) {
    uint8_t cmd, val;
    uint16_t count, i;
    uint16_t reg;

    CPU_PRESCALE(0);
    LED_CONFIG;

    uart_init(57600);

    while (1) {

        cmd = uart_getchar();

        // determine how many bytes to read or write
        if (cmd & SMALL_COUNT_MASK)
            count = cmd & COUNT_MASK;
        else
            count = ((cmd & COUNT_MASK) << 8) + uart_getchar();

        // filter actual command
        cmd = cmd & CMD_MASK;

        reg = uart_getchar();

        switch (cmd) {
            case (CMD_READ_IO8):
                for (i = 0; i < count; i++)
                    uart_putchar(_SFR_IO8(reg));
                break;
            case (CMD_WRITE_IO8):
                for (i = 0; i < count; i++) {
                    val = uart_getchar();
                    _SFR_IO8(reg) = val;
                }
                break;
            case (CMD_READ_MEM8):
                for (i = 0; i < count; i++)
                    uart_putchar(_SFR_MEM8(reg));
                break;
            case CMD_WRITE_MEM8:
                for (i = 0; i < count; i++) {
                    val = uart_getchar();
                    _SFR_MEM8(reg) = val;
                }
                break;
            default:
                break;
                // TODO some error handling would be nice
        }
    }
}
