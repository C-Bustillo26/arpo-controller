from src.display.lcd_display import LCDDisplay
import time

lcd = LCDDisplay()

if lcd.enabled:
    lcd.show_message("ARPO System", "LCD Test OK")
    time.sleep(10)
    lcd.cleanup()
else:
    print("LCD not available")
