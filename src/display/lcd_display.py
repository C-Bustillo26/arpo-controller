import time
from .lcd_driver import LCDDriver


class LCDDisplay:
    def __init__(self):
        self.enabled = False
        self.driver = None

        try:
            self.driver = LCDDriver()
            self.enabled = True
            self.show_message("ARPO System", "LCD Ready")
            time.sleep(1)
            self.clear()
            print("[LCD] LCD initialized.")
        except Exception as e:
            print(f"[LCD] LCD unavailable: {e}")
            self.enabled = False

    def clear(self):
        if self.enabled and self.driver:
            self.driver.clear()

    def show_message(self, line1: str, line2: str = ""):
        if not self.enabled or not self.driver:
            return
        self.driver.write_line(line1, 1)
        self.driver.write_line(line2, 2)

    def show_status(self, grid_failed, battery_low, relay_state, inverter_state):
        line1 = "GRID:FAIL" if grid_failed else "GRID:ON"
        line2 = "BATT:LOW" if battery_low else "BATT:OK"
        self.show_message(line1, line2)

    def show_mode(self, relay_state, inverter_state):
        relay_text = f"R:{relay_state}" if relay_state else "R:UNK"
        inverter_text = f"I:{inverter_state}"
        self.show_message(relay_text[:16], inverter_text[:16])

    def cleanup(self):
        self.clear()
