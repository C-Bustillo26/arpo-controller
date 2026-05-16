# ============================================================
# ADS1263 ADC reader for ARPO.
# ============================================================

import sys
from pathlib import Path

from app_config.settings import (
    ADC_DRIVER_PATH,
    ADC_DRIVER_PATH_FALLBACK,
    ADC_RATE,
    ADC_SAMPLE_COUNT,
    REF,
    CHANNEL_SETTINGS,
    A_V,
    B_V,
    K_GRID_V,
    K_BACKUP_V,
    K_GRID_I,
    K_BACKUP_I,
    TEST_MODE,
)

from .sensing.voltage_current_sensing import VoltageCurrentSensing


class ADCReader:

    # ============================================================
    # Reads and processes all ARPO ADC channels.
    # ============================================================

    def __init__(self):
        self.test_mode = TEST_MODE
        self.adc = None
        self.sensing = None

        if self.test_mode:
            print(f"[ADC] TEST_MODE enabled: {self.test_mode}")
            return
	
	# ============================================================
        # Add the Waveshare ADS1263 driver folder to Python's import path.
	# ============================================================

        driver_path = Path(ADC_DRIVER_PATH)
        if not driver_path.exists():
            driver_path = Path(ADC_DRIVER_PATH_FALLBACK)
        if not driver_path.exists():
            raise FileNotFoundError(
                f"[ADC ERROR] ADS1263 driver path not found. Tried "
                f"{ADC_DRIVER_PATH} and {ADC_DRIVER_PATH_FALLBACK}"
            )

        sys.path.insert(0, str(driver_path))
        import ADS1263  # type: ignore

        print("[ADC] Initializing ADS1263...")
        self.adc = ADS1263.ADS1263()

        if self.adc.ADS1263_init_ADC1(ADC_RATE) == -1:
            raise RuntimeError("[ADC] Initialization failed.")

        self.adc.ADS1263_SetMode(0)

	# ============================================================
        # RMS processor uses the tested reference voltage, sample count, and
        # calibration constants from settings.py.
	# ============================================================

        self.sensing = VoltageCurrentSensing(
            adc=self.adc,
            ref=REF,
            sample_count=ADC_SAMPLE_COUNT,
            voltage_correction_a=A_V,
            voltage_correction_b=B_V,
        )

        print("[ADC] Initialization complete.")

    def _fake_value(self, name):

	# ============================================================
        # Return fake values for software testing only.
	# ============================================================

        test_values = {
            "GRID": {
                "grid_voltage": 120.0,
                "grid_current": 0.80,
                "backup_voltage": 0.0,
                "backup_current": 0.0,
            },
            "BACKUP": {
                "grid_voltage": 0.0,
                "grid_current": 0.0,
                "backup_voltage": 118.0,
                "backup_current": 0.75,
            },
            "FAULT": {
                "grid_voltage": 0.0,
                "grid_current": 0.0,
                "backup_voltage": 60.0,
                "backup_current": 0.50,
            },
        }
        values = test_values.get(self.test_mode, test_values["GRID"])
        return values[name]

    def read_named_channel(self, name):

	# ============================================================
	# Read one named channel and return scaled engineering units.
	# ============================================================

        if self.test_mode:
            return self._fake_value(name)

        for channel, config in CHANNEL_SETTINGS.items():
            if config["name"] != name:
                continue

            if name == "grid_voltage":
                return self.sensing.process_voltage(channel, K_GRID_V)
            if name == "backup_voltage":
                return self.sensing.process_voltage(channel, K_BACKUP_V)

            # ============================================================
            # Current scaling is tunable in app_config/settings.py.
            # ============================================================

            if name == "grid_current":
                return self.sensing.process_current(channel, K_GRID_I)
            if name == "backup_current":
                return self.sensing.process_current(channel, K_BACKUP_I)

        raise ValueError(f"[ADC ERROR] No configured channel named: {name}")

    def debug_current_channel(self, name):

	# ============================================================
	# Return raw diagnostic values for grid_current or backup_current.
	# ============================================================

        if self.test_mode:
            return {
                "channel": -1,
                "min_v": 0.0,
                "max_v": 0.0,
                "mean_v": 0.0,
                "pi_irms_v": 0.0,
                "scale_factor": 1.0,
                "final_a": self._fake_value(name),
            }

        for channel, config in CHANNEL_SETTINGS.items():
            if config["name"] != name:
                continue
            if name == "grid_current":
                return self.sensing.process_current_debug(channel, K_GRID_I)
            if name == "backup_current":
                return self.sensing.process_current_debug(channel, K_BACKUP_I)

        raise ValueError(f"[ADC ERROR] No configured current channel named: {name}")

    def read_all(self):

	# ============================================================
	# Read all four ARPO measurement channels.
	# ============================================================

        return {
            "grid_voltage": self.read_named_channel("grid_voltage"),
            "grid_current": self.read_named_channel("grid_current"),
            "backup_voltage": self.read_named_channel("backup_voltage"),
            "backup_current": self.read_named_channel("backup_current"),
        }

    def close(self):

	# ============================================================
	# Shut down the ADC driver if supported.
	# ============================================================

        if self.adc is None:
            return
        try:
            self.adc.ADS1263_Exit()
            print("[ADC] Shutdown complete.")
        except Exception:
            pass
