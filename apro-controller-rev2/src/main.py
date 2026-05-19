# ============================================================
# Main ARPO integration controller.
# ============================================================

import logging
import time
from pathlib import Path
from datetime import datetime

from app_config.settings import (
    BACKUP_MIN_VOLTAGE_AC,
    BACKUP_STARTUP_GRACE_SECONDS,
    GRID_FAIL_VOLTAGE_AC,
    GRID_RESTORE_VOLTAGE_AC,
    GRID_LOW_COUNT_REQUIRED,
    GRID_RESTORE_COUNT_REQUIRED,
    GPIO_LOGIC_TEST_IGNORE_BACKUP_LOW,
    LOG_FOLDER,
    MAX_LOAD_CURRENT_A,
    OUTAGE_CONFIRM_SECONDS,
    POLL_INTERVAL,
    RESTORE_CONFIRM_SECONDS,
    TRANSFER_DELAY,
)

from .adc_reader import ADCReader
from .display.lcd_display import LCDDisplay
from .inverter.inverter_control import InverterController
from .relay_control import RelayController
from .utils import timestamp


LOG_DIR = Path(LOG_FOLDER)
LOG_DIR.mkdir(exist_ok=True)
RUN_LOG_FILE = LOG_DIR / f"arpo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

logging.basicConfig(
    filename=str(RUN_LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

print(f"[LOG] Writing run log to {RUN_LOG_FILE}")


def log_and_print(message: str):

    # ============================================================
    # Print a message to terminal and write it to the run log.
    # ============================================================

    print(message)
    logging.info(message)


def read_measurements(adc_reader):

    # ============================================================
    # Read all voltage/current channels with RMS processing.
    # ============================================================

    return adc_reader.read_all()


def update_lcd(lcd, mode, values, inverter, event="", fault=""):

    # ============================================================
    # Update the LCD display if it is available.
    # ============================================================

    if not lcd.enabled:
        return

    lcd.show_status(
        mode=mode,
        grid_voltage=values["grid_voltage"],
        grid_current=values["grid_current"],
        backup_voltage=values["backup_voltage"],
        backup_current=values["backup_current"],
        inverter_state=inverter.status(),
        event=event,
        fault=fault,
    )


def status_message(mode, values, relay, inverter, event):

    # ============================================================
    # Build one readable terminal/log status line.
    # ============================================================

    return (
        f"[{timestamp()}] "
        f"Mode: {mode} | "
        f"Grid Voltage: {values['grid_voltage']:.1f} VAC | "
        f"Grid Current: {values['grid_current']:.6f} A | "
        f"Backup Voltage: {values['backup_voltage']:.1f} VAC | "
        f"Backup Current: {values['backup_current']:.6f} A | "
        f"Relay: {relay.current_state if relay.current_state else 'UNKNOWN'} | "
        f"Inverter: {inverter.status()} | "
        f"Event: {event}"
    )


def start_backup_sequence(adc_reader, relay, inverter, lcd):

    # ============================================================
    # Start backup mode and validate the inverter output after startup.
    # ============================================================

    log_and_print("[ARPO] Backup sequence starting.")
    log_and_print("[TIMING] Inverter start command issued.")

    # ============================================================
    # The inverter must be running before backup voltage can be measured.
    # ============================================================

    inverter.start()
    time.sleep(TRANSFER_DELAY)

    log_and_print("[TIMING] Relay transfer to BACKUP command issued.")
    relay.switch_to_backup()

    start_time = time.time()
    latest_values = read_measurements(adc_reader)

    # ============================================================
    # Allow the inverter/transformer output to build before backup voltage is
    # treated as valid.
    # ============================================================

    while time.time() - start_time < BACKUP_STARTUP_GRACE_SECONDS:
        latest_values = read_measurements(adc_reader)
        update_lcd(
            lcd=lcd,
            mode="STARTING",
            values=latest_values,
            inverter=inverter,
            event="Backup starting",
        )
        log_and_print(
            status_message(
                mode="STARTING",
                values=latest_values,
                relay=relay,
                inverter=inverter,
                event="Backup stabilizing",
            )
        )
        time.sleep(POLL_INTERVAL)

    latest_values = read_measurements(adc_reader)

    # ============================================================
    # During GPIO-only tests, backup voltage may intentionally be 0 V because
    # the MOSFET gates, transformer, or output wiring may be disconnected.
    # ============================================================

    if latest_values["backup_voltage"] < BACKUP_MIN_VOLTAGE_AC:
        if GPIO_LOGIC_TEST_IGNORE_BACKUP_LOW:
            return "BACKUP", latest_values, "Backup low ignored for test", ""
        return "FAULT", latest_values, "Backup voltage low", "LOW BACKUP"

    if latest_values["backup_current"] > MAX_LOAD_CURRENT_A:
        return "FAULT", latest_values, "Backup overcurrent", "OVERCURRENT"

    return "BACKUP", latest_values, "Backup running", ""


def return_to_grid(relay, inverter):

    # ============================================================
    # Return to grid with a soft inverter shutdown sequence.
    # Stop inverter first so the relay is not transferring while the inverter is
    # actively driving the transformer.
    # ============================================================

    inverter.stop()
    time.sleep(TRANSFER_DELAY)
    relay.switch_to_grid()


def main():

    # ============================================================
    # Run the main ARPO controller.
    # ============================================================

    adc_reader = ADCReader()
    relay = RelayController()
    inverter = InverterController()

    log_and_print("ARPO integration controller started.")

    # ============================================================
    # Safe startup defaults.
    # ============================================================

    relay.switch_to_grid()
    inverter.stop()
    time.sleep(1)

    lcd = LCDDisplay()
    if lcd.enabled:
        lcd.show_message("ARPO STARTING", "Init...")
        time.sleep(1)
    else:
        log_and_print("[LCD] LCD unavailable. Continuing without display.")

    mode = "GRID"
    outage_start = None
    restore_start = None
    outage_timer_start = None
    restore_timer_start = None
    grid_low_count = 0
    grid_restore_count = 0

    try:
        while True:
            now = time.time()

            # ============================================================
            # Full ADC reads are used in the main controller so voltage and
            # current values shown on the LCD and logs are always real readings.
            # ============================================================

            values = read_measurements(adc_reader)
            event = ""
            fault = ""

            if (
                values["grid_current"] > MAX_LOAD_CURRENT_A
                or values["backup_current"] > MAX_LOAD_CURRENT_A
            ):
                mode = "FAULT"
                event = "Overcurrent detected"
                fault = "OVERCURRENT"
                return_to_grid(relay, inverter)

            elif mode == "GRID":
                if values["grid_voltage"] < GRID_FAIL_VOLTAGE_AC:
                    grid_low_count += 1

                    if outage_timer_start is None:
                        outage_timer_start = now
                        log_and_print(
                            f"[TIMING] Outage timer started. Grid={values['grid_voltage']:.1f} VAC"
                        )

                    if outage_start is None:
                        outage_start = now

                    if (
                        grid_low_count >= GRID_LOW_COUNT_REQUIRED
                        and now - outage_start >= OUTAGE_CONFIRM_SECONDS
                    ):
                        grid_low_count = 0
                        grid_restore_count = 0
                        mode, values, event, fault = start_backup_sequence(
                            adc_reader=adc_reader,
                            relay=relay,
                            inverter=inverter,
                            lcd=lcd,
                        )

                        if outage_timer_start is not None:
                            transfer_time = time.time() - outage_timer_start
                            log_and_print(
                                f"[TIMING] SOFTWARE TRANSFER TIME = {transfer_time:.3f} seconds"
                            )
                    else:
                        event = f"Outage timing {grid_low_count}/{GRID_LOW_COUNT_REQUIRED}"

                else:
                    grid_low_count = 0
                    outage_start = None
                    outage_timer_start = None
                    event = "Grid normal"

            elif mode == "BACKUP":
                if values["grid_voltage"] >= GRID_RESTORE_VOLTAGE_AC:
                    grid_restore_count += 1

                    if restore_timer_start is None:
                        restore_timer_start = now
                        log_and_print(
                            f"[TIMING] Restore timer started. Grid={values['grid_voltage']:.1f} VAC"
                        )

                    if restore_start is None:
                        restore_start = now

                    if (
                        grid_restore_count >= GRID_RESTORE_COUNT_REQUIRED
                        and now - restore_start >= RESTORE_CONFIRM_SECONDS
                    ):
                        return_to_grid(relay, inverter)
                        mode = "GRID"
                        event = "Grid restored"

                        if restore_timer_start is not None:
                            restore_time = time.time() - restore_timer_start
                            log_and_print(
                                f"[TIMING] SOFTWARE RESTORE TIME = {restore_time:.3f} seconds"
                            )

                        restore_start = None
                        restore_timer_start = None
                        outage_timer_start = None
                        grid_restore_count = 0
                        grid_low_count = 0
                    else:
                        event = f"Restore timing {grid_restore_count}/{GRID_RESTORE_COUNT_REQUIRED}"

                elif values["backup_voltage"] < BACKUP_MIN_VOLTAGE_AC:
                    if GPIO_LOGIC_TEST_IGNORE_BACKUP_LOW:
                        restore_start = None
                        restore_timer_start = None
                        grid_restore_count = 0
                        event = "Backup low ignored for test"
                    else:
                        mode = "FAULT"
                        event = "Backup voltage low"
                        fault = "LOW BACKUP"
                        return_to_grid(relay, inverter)

                else:
                    restore_start = None
                    restore_timer_start = None
                    grid_restore_count = 0
                    event = "Backup running"

            elif mode == "FAULT":
                if values["grid_voltage"] >= GRID_RESTORE_VOLTAGE_AC:
                    if restore_start is None:
                        restore_start = now

                    if now - restore_start >= RESTORE_CONFIRM_SECONDS:
                        return_to_grid(relay, inverter)
                        mode = "GRID"
                        event = "Fault cleared, grid normal"
                        fault = ""
                        restore_start = None
                    else:
                        event = "Fault reset timing"
                        fault = "WAIT GRID"
                else:
                    event = "Fault active"
                    fault = fault or "CHECK SYSTEM"

            update_lcd(lcd, mode, values, inverter, event, fault)
            log_and_print(status_message(mode, values, relay, inverter, event))
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        log_and_print("Stopping ARPO integration controller.")

    finally:
        return_to_grid(relay, inverter)

        if lcd.enabled:
            lcd.show_message("SYSTEM STOP", "GRID SELECTED")
            time.sleep(1)
            lcd.cleanup()

        log_and_print(f"[LOG] Run log saved to {RUN_LOG_FILE}")
        adc_reader.close()

        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except Exception:
            pass


if __name__ == "__main__":
    main()
