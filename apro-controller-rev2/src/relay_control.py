# ============================================================
# DPDT relay control for grid/backup source selection.
# ============================================================

import RPi.GPIO as GPIO

from app_config.settings import RELAY_GPIO, RELAY_GRID_STATE, RELAY_BACKUP_STATE


class RelayController:

    # ============================================================
    # Controls the DPDT relay used to select grid or inverter output.
    # ============================================================

    def __init__(self, pin=RELAY_GPIO):
        self.pin = pin
        self.current_state = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)

	# ============================================================
	# Start in grid position so utility and inverter are not unintentionally
	# connected during startup.
	# ============================================================

        self.switch_to_grid()
        print(f"[Relay] Initialized on GPIO {self.pin}")

    def switch_to_grid(self):

	# ============================================================
	# Select grid/utility power.
	# ============================================================

        GPIO.output(self.pin, RELAY_GRID_STATE)
        self.current_state = "GRID"
        print("[Relay] Switched to GRID / UTILITY power")

    def switch_to_backup(self):

	# ============================================================
	# Select inverter/backup power.
	# ============================================================

        GPIO.output(self.pin, RELAY_BACKUP_STATE)
        self.current_state = "BACKUP"
        print("[Relay] Switched to BACKUP / INVERTER power")

    def switch_to_battery(self):
	
	# ============================================================
	# Compatibility alias for previous versions of code.
	# ============================================================

        self.switch_to_backup()

    def cleanup(self):

	# ============================================================
	# Return relay to grid and release the relay GPIO.
	# ============================================================

        try:
            self.switch_to_grid()
        finally:
            GPIO.cleanup(self.pin)
            print("[Relay] GPIO cleanup complete")
