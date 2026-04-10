import logging
import time
from .adc_reader import ADCReader
from .grid_monitor import is_grid_on, read_grid_voltage
from .battery_monitor import read_battery_voltage, is_battery_low
from .relay_control import RelayController
from .utils import timestamp
from app_config.settings import POLL_INTERVAL


logging.basicConfig(
    filename="arpo_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
) 


def main():
    adc_reader = ADCReader()
    relay = RelayController()

    print("ARPO controller started.")

    try:
        while True:
            grid_voltage = read_grid_voltage(adc_reader)
            battery_voltage = read_battery_voltage(adc_reader)

            grid_status = is_grid_on(adc_reader)
            battery_low = is_battery_low(adc_reader)

            print(
                f"[{timestamp()}] "
                f"Grid Voltage: {grid_voltage:.3f} V | "
                f"Battery Voltage: {battery_voltage:.3f} V | "
                f"Grid: {'ON' if grid_status else 'OFF'} | "
                f"Battery Low: {'YES' if battery_low else 'NO'}"
            )

            if grid_status:
                relay.switch_to_grid()
            else:
                relay.switch_to_backup()

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping ARPO controller.")
        relay.cleanup()
        adc_reader.close()


if __name__ == "__main__":
    main()
