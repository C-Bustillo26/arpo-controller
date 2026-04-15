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

bus = smbus.SMBus(1)


def lcd_init():
    time.sleep(0.02)

    lcd_byte(0x03, LCD_CMD)
    time.sleep(0.005)
    lcd_byte(0x03, LCD_CMD)
    time.sleep(0.0002)
    lcd_byte(0x03, LCD_CMD)

    lcd_byte(0x02, LCD_CMD)

    lcd_byte(0x28, LCD_CMD)  # 4-bit mode
    lcd_byte(0x0C, LCD_CMD)  # display ON
    lcd_byte(0x06, LCD_CMD)  # entry mode
    lcd_byte(0x01, LCD_CMD)  # clear
    time.sleep(0.005)


def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, bits | ENABLE)
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)
    time.sleep(E_DELAY)


def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)
