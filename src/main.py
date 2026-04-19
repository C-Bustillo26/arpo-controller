import time
import logging

from .adc_reader import ADCReader
from .relay_control import RelayController
from .inverter.inverter_stub import InverterController
from .display.lcd_display import LCDDisplay
from .utils import timestamp
from app_config.settings import POLL_INTERVAL, LOG_FILE


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

# Weekly integration thresholds
GRID_FAIL_THRESHOLD_ADC = 4.17
GRID_RESTORE_THRESHOLD_ADC = 4.58
BATTERY_LOW_THRESHOLD = 4.8

# Test modes: NONE, "GRID", "BACKUP", "FAULT"
TEST_MODE =None 

def log_and_print(message: str):
    print(message)
    logging.info(message)


def determine_mode(grid_failed: bool, battery_low: bool) -> str:
    if not grid_failed:
        return "GRID"
    if grid_failed and not battery_low:
        return "BACKUP"
    return "FAULT"


def main():
    adc_reader = ADCReader()
    relay = RelayController()
    inverter = InverterController()

    log_and_print("ARPO weekly integration started.")

    # Safe startup defaults first
    relay.switch_to_grid()
    inverter.stop()
    time.sleep(2)

    # Bring up LCD after everything else settles
    lcd = LCDDisplay()

    if lcd.enabled:
        lcd.show_message("ARPO STARTING", "Init...")
        time.sleep(1)
    else:
        log_and_print("[LCD] LCD unavailable. Continuing without display.")

    try:
        while True:
            # Read each ADC channel once per loop
            grid_voltage = adc_reader.read_named_channel("grid_voltage")
            grid_current = adc_reader.read_named_channel("grid_current")
            battery_voltage = adc_reader.read_named_channel("battery_voltage")
            battery_current = adc_reader.read_named_channel("battery_current")

            # Weekly demo logic
            grid_failed = grid_voltage < GRID_FAIL_THRESHOLD_ADC
            grid_restored = grid_voltage > GRID_RESTORE_THRESHOLD_ADC
            battery_low = battery_voltage < BATTERY_LOW_THRESHOLD

            # Temporary test override
            if TEST_MODE == "GRID":
               grid_failed = False
               battery_low = False
            elif TEST_MODE == "BACKUP":
               grid_failed = True
               battery_low = False
            elif TEST_MODE == "FAULT":
               grid_failed = True
               battery_low = True

            mode = determine_mode(grid_failed, battery_low)

            # Control relay + inverter stub
            if mode == "GRID":
                relay.switch_to_grid()
                inverter.stop()
            elif mode == "BACKUP":
                inverter.start()
                relay.switch_to_battery()
            elif mode == "FAULT":
                inverter.stop()

            message = (
                f"[{timestamp()}] "
                f"Mode: {mode} | "
                f"Grid Voltage: {grid_voltage:.3f} V | "
                f"Grid Current: {grid_current:.3f} A | "
                f"Battery Voltage: {battery_voltage:.3f} V | "
                f"Battery Current: {battery_current:.3f} A | "
                f"Grid Failed: {'YES' if grid_failed else 'NO'} | "
                f"Grid Restored: {'YES' if grid_restored else 'NO'} | "
                f"Battery Low: {'YES' if battery_low else 'NO'} | "
                f"Relay: {relay.current_state if relay.current_state else 'UNKNOWN'} | "
                f"Inverter: {inverter.status()}"
            )
            log_and_print(message)

            if lcd.enabled:
                lcd.show_status(
                    mode=mode,
                    grid_failed=grid_failed,
                    battery_low=battery_low,
                    inverter_state=inverter.status()
                )

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        log_and_print("Stopping ARPO weekly integration.")

        if lcd.enabled:
            lcd.show_message("SYSTEM STOP", "Shutting down")
            time.sleep(1)
            lcd.cleanup()

        relay.cleanup()
        adc_reader.close()


if __name__ == "__main__":
    main()
