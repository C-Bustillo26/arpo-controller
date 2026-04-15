import smbus
import time

I2C_ADDR = 0x27
LCD_WIDTH = 16

LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100

E_PULSE = 0.0005
E_DELAY = 0.0005


class LCDDriver:
    def __init__(self, addr=I2C_ADDR, bus_num=1):
        self.addr = addr
        self.bus = smbus.SMBus(bus_num)
        self.lcd_init()

    def lcd_init(self):
        time.sleep(0.02)

        self.lcd_byte(0x33, LCD_CMD)
        self.lcd_byte(0x32, LCD_CMD)
        self.lcd_byte(0x06, LCD_CMD)
        self.lcd_byte(0x0C, LCD_CMD)
        self.lcd_byte(0x28, LCD_CMD)
        self.lcd_byte(0x01, LCD_CMD)
        time.sleep(E_DELAY)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

        self.bus.write_byte(self.addr, bits_high)
        self.lcd_toggle_enable(bits_high)

        self.bus.write_byte(self.addr, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(E_DELAY)
        self.bus.write_byte(self.addr, bits | ENABLE)
        time.sleep(E_PULSE)
        self.bus.write_byte(self.addr, bits & ~ENABLE)
        time.sleep(E_DELAY)

    def clear(self):
        self.lcd_byte(0x01, LCD_CMD)
        time.sleep(E_DELAY)

    def write_line(self, message: str, line: int):
        message = message[:LCD_WIDTH].ljust(LCD_WIDTH, " ")

        if line == 1:
            self.lcd_byte(LCD_LINE_1, LCD_CMD)
        elif line == 2:
            self.lcd_byte(LCD_LINE_2, LCD_CMD)
        else:
            raise ValueError("LCD line must be 1 or 2")

        for char in message:
            self.lcd_byte(ord(char), LCD_CHR)
