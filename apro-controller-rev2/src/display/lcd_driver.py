# ============================================================
# Basic 16x2 I2C LCD driver for a PCF8574 backpack.
# ============================================================

import time

import smbus

from app_config.settings import LCD_I2C_ADDRESS, LCD_COLUMNS


LCD_CHR = 1
LCD_CMD = 0
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100
E_PULSE = 0.0005
E_DELAY = 0.0005


class LCDDriver:
    
	# ============================================================
	# Low-level HD44780 16x2 LCD over I2C.
	# ============================================================

    def __init__(self, addr=LCD_I2C_ADDRESS, bus_num=1):
        self.addr = addr
        self.bus = smbus.SMBus(bus_num)
        self.lcd_init()

    def lcd_init(self):

	# ============================================================
        # Initialize LCD in 4-bit mode.
	# ============================================================

        time.sleep(0.02)
        self.lcd_byte(0x33, LCD_CMD)
        self.lcd_byte(0x32, LCD_CMD)
        self.lcd_byte(0x06, LCD_CMD)
        self.lcd_byte(0x0C, LCD_CMD)
        self.lcd_byte(0x28, LCD_CMD)
        self.lcd_byte(0x01, LCD_CMD)
        time.sleep(E_DELAY)

    def lcd_byte(self, bits, mode):

	# ============================================================
        # Send one byte to LCD as two 4-bit writes.
	# ============================================================

        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
        self.bus.write_byte(self.addr, bits_high)
        self.lcd_toggle_enable(bits_high)
        self.bus.write_byte(self.addr, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):

	# ============================================================
        # Toggle LCD enable bit.
	# ============================================================

        time.sleep(E_DELAY)
        self.bus.write_byte(self.addr, bits | ENABLE)
        time.sleep(E_PULSE)
        self.bus.write_byte(self.addr, bits & ~ENABLE)
        time.sleep(E_DELAY)

    def clear(self):

	# ============================================================
        # Clear LCD display.
	# ============================================================

        self.lcd_byte(0x01, LCD_CMD)
        time.sleep(E_DELAY)

    def write_line(self, message: str, line: int):

	# ============================================================
        # Write one padded 16-character line to the LCD.
	# ============================================================
	
        message = message[:LCD_COLUMNS].ljust(LCD_COLUMNS, " ")
        if line == 1:
            self.lcd_byte(LCD_LINE_1, LCD_CMD)
        elif line == 2:
            self.lcd_byte(LCD_LINE_2, LCD_CMD)
        else:
            raise ValueError("LCD line must be 1 or 2")

        for char in message:
            self.lcd_byte(ord(char), LCD_CHR)
