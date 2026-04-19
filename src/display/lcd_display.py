import time
from .lcd_driver import LCDDriver


class LCDDisplay:
    def __init__(self):
        self.enabled = False
        self.driver = None

        # Give the LCD bus a moment before first access
        time.sleep(1)

        for attempt in range(3):
            try:
                self.driver = LCDDriver()
                self.enabled = True
                self.show_message("ARPO System", "LCD Ready")
                time.sleep(1)
                self.clear()
                print("[LCD] LCD initialized.")
                break
            except Exception as e:
                print(f"[LCD] Init attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        if not self.enabled:
            print("[LCD] LCD unavailable after retries.")

    def clear(self):
        if self.enabled and self.driver:
            self.driver.clear()

    def show_message(self, line1: str, line2: str = ""):
        if not self.enabled or not self.driver:
            return
        self.driver.write_line(line1, 1)
        self.driver.write_line(line2, 2)

    def show_status(self, mode, grid_failed, battery_low, inverter_state):
        line1 = f"MODE:{mode}"[:16]

        if mode == "GRID":
            line2 = "GRID OK BATT OK"
        elif mode == "BACKUP":
            line2 = "GRID FAIL INV ON"
        elif mode == "FAULT":
            line2 = "BATT LOW"
        else:
            line2 = f"INV:{inverter_state}"

        self.show_message(line1[:16], line2[:16])

    def cleanup(self):
        self.clear()
