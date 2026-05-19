# ============================================================
# Rotating 16x2 LCD status pages for ARPO.
# ============================================================

import time

from app_config.settings import LCD_PAGE_SECONDS

from .lcd_driver import LCDDriver


class LCDDisplay:

    # ============================================================
    # High-level LCD display helper.
    # ============================================================

    def __init__(self):
        self.enabled = False
        self.driver = None
        self.page = 0
        self.last_page_change = time.time()

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
            except Exception as exc:
                print(f"[LCD] Init attempt {attempt + 1} failed: {exc}")
                time.sleep(1)

        if not self.enabled:
            print("[LCD] LCD unavailable after retries.")

    def clear(self):

        # ============================================================
        # Clear LCD if enabled.
        # ============================================================

        if self.enabled and self.driver:
            self.driver.clear()

    def show_message(self, line1: str, line2: str = ""):

        # ============================================================
        # Write two lines to the LCD.
        # ============================================================

        if not self.enabled or not self.driver:
            return

        self.driver.write_line(line1, 1)
        self.driver.write_line(line2, 2)

    # ============================================================
    # Added all of the ADC input readings.
    # ============================================================

    def show_status(
        self,
        mode,
        grid_voltage,
        grid_current,
        backup_voltage,
        backup_current,
        inverter_state,
        event="",
        fault="",
    ):
        # ============================================================
        # Show rotating compact ARPO status pages.
        # ============================================================

        if mode == "FAULT":
            self.show_message("!!! FAULT !!!", fault[:16] if fault else "CHECK SYSTEM")
            return

        now = time.time()

        if now - self.last_page_change >= LCD_PAGE_SECONDS:
            self.page = (self.page + 1) % 4
            self.last_page_change = now

        if self.page == 0:
            line1 = f"GRID:{grid_voltage:5.1f}V"
            line2 = f"CURR:{grid_current:5.2f}A"
        elif self.page == 1:
            line1 = f"BACK:{backup_voltage:5.1f}V"
            line2 = f"CURR:{backup_current:5.2f}A"
        elif self.page == 2:
            line1 = f"MODE:{mode}"
            line2 = f"INV:{inverter_state}"
        else:
            line1 = "STATUS:NORMAL"
            line2 = event[:16] if event else "NO EVENT"

        self.show_message(line1[:16], line2[:16])

    def cleanup(self):

        # ============================================================
        # Clear LCD on shutdown.
        # ============================================================

        self.clear()