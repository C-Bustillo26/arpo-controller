import time
import logging

from .adc_reader import ADCReader
from .grid_monitor import (
    read_grid_voltage,
    read_grid_current,
    is_grid_failed,
    is_grid_restorable,
)
from .battery_monitor import (
    read_battery_voltage,
    read_battery_current,
    is_battery_low,
)
from .relay_control import RelayController
from .inverter.inverter_control import InverterController
from .display.lcd_display import LCDDisplay
from .utils import timestamp
from app_config.settings import POLL_INTERVAL, LOG_FILE, TRANSFER_DELAY


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)


def log_and_print(message: str):
    print(message)
    logging.info(message)


def get_grid_frequency():
    """
    Placeholder for future real frequency sensing.
    Replace this later with actual measured frequency.
    """
    return 60.0


def switch_to_backup(relay, inverter, lcd):
    log_and_print("[System] Grid failed. Starting backup transfer sequence.")

    if lcd.enabled:
        lcd.show_message("GRID FAIL", "SWITCH BACKUP")
        time.sleep(1)

    inverter.start()
    time.sleep(TRANSFER_DELAY)

    relay.switch_to_battery()
    time.sleep(TRANSFER_DELAY)

    log_and_print("[System] Backup transfer complete.")

    if lcd.enabled:
        lcd.show_message("MODE: BACKUP", "LOAD PROTECTED")
        time.sleep(1)


def switch_to_grid(relay, inverter, lcd):
    log_and_print("[System] Grid stable. Starting return-to-grid sequence.")

    if lcd.enabled:
        lcd.show_message("GRID RESTORED", "RETURN GRID")
        time.sleep(1)

    relay.switch_to_grid()
    time.sleep(TRANSFER_DELAY)

    inverter.stop()
    time.sleep(TRANSFER_DELAY)

    log_and_print("[System] Return-to-grid complete.")

    if lcd.enabled:
        lcd.show_message("MODE: GRID", "INVERTER OFF")
        time.sleep(1)


def main():
    adc_reader = ADCReader()
    relay = RelayController()
    inverter = InverterController()
    lcd = LCDDisplay()

    system_mode = None

    log_and_print("ARPO controller started.")

    if lcd.enabled:
        lcd.show_message("ARPO STARTING", "Initializing...")
        time.sleep(2)
    else:
        log_and_print("[LCD] LCD unavailable. Continuing without display.")

    try:
        while True:
            grid_voltage = read_grid_voltage(adc_reader)
            grid_current = read_grid_current(adc_reader)
            battery_voltage = read_battery_voltage(adc_reader)
            battery_current = read_battery_current(adc_reader)

            battery_low = is_battery_low(adc_reader)

            grid_frequency = get_grid_frequency()

            grid_failed = is_grid_failed(adc_reader)
            grid_restorable = is_grid_restorable(adc_reader, grid_frequency)

            message = (
                f"[{timestamp()}] "
                f"Grid Voltage: {grid_voltage:.3f} V | "
                f"Grid Current: {grid_current:.3f} A | "
                f"Battery Voltage: {battery_voltage:.3f} V | "
                f"Battery Current: {battery_current:.3f} A | "
                f"Grid Failed: {'YES' if grid_failed else 'NO'} | "
                f"Grid Frequency: {grid_frequency:.2f} Hz | "
                f"Grid Restorable: {'YES' if grid_restorable else 'NO'} | "
                f"Battery Low: {'YES' if battery_low else 'NO'} | "
                f"Relay: {relay.current_state if relay.current_state else 'UNKNOWN'} | "
                f"Inverter: {inverter.status()}"
            )
            log_and_print(message)

            if lcd.enabled:
                lcd.show_status(
                    grid_failed=grid_failed,
                    battery_low=battery_low,
                    relay_state=relay.current_state,
                    inverter_state=inverter.status()
                )

            if grid_failed:
                if battery_low:
                    log_and_print("[WARNING] Grid is down and battery is low. Backup transfer blocked.")
                    if lcd.enabled:
                        lcd.show_message("GRID DOWN", "BATTERY LOW")
                else:
                    if system_mode != "BACKUP":
                        switch_to_backup(relay, inverter, lcd)
                        system_mode = "BACKUP"
            else:
                if grid_restorable:
                    if system_mode != "GRID":
                        switch_to_grid(relay, inverter, lcd)
                        system_mode = "GRID"

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        log_and_print("Stopping ARPO controller.")

        if lcd.enabled:
            lcd.show_message("SYSTEM STOP", "Shutting down")
            time.sleep(1)
            lcd.cleanup()

        relay.cleanup()
        adc_reader.close()


if __name__ == "__main__":
    main()
