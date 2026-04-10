import RPi.GPIO as GPIO
from app_config.settings import RELAY_GPIO


class RelayController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_GPIO, GPIO.OUT)

        self.current_state = None

        print(f"[Relay] Initialized on GPIO {RELAY_GPIO}")

    def switch_to_grid(self):
        if self.current_state != "GRID":
            GPIO.output(RELAY_GPIO, GPIO.LOW)
            self.current_state = "GRID"
            print("[Relay] Switched to GRID power")

    def switch_to_battery(self):
        if self.current_state != "BATTERY":
            GPIO.output(RELAY_GPIO, GPIO.HIGH)
            self.current_state = "BATTERY"
            print("[Relay] Switched to BATTERY power")

    def cleanup(self):
        GPIO.cleanup()
        print("[Relay] GPIO cleanup complete")
