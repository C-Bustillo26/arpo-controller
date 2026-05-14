import sys
from pathlib import Path

# Add Waveshare ADC library path dynamically
LIB_PATH = Path.home() / "High-Pricision_AD_HAT" / "python"

if not LIB_PATH.exists():
    raise FileNotFoundError(
        f"[ERROR] Waveshare ADC library not found at: {LIB_PATH}\n"
        "Make sure you cloned the Waveshare repo correctly."
    )

sys.path.insert(0, str(LIB_PATH))

import ADS1263  # type: ignore
from app_config.settings import CHANNEL_SETTINGS


class ADCReader:
    def __init__(self):
        print("[ADC] Initializing ADS1263...")

        self.adc = ADS1263.ADS1263()

        if self.adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1:
            raise RuntimeError("[ADC] Initialization failed!")

        self.channels = sorted(CHANNEL_SETTINGS.keys())

        # ADS1263 settings
        self.vref = 5.08      # adjust if your board/reference is different
        self.full_scale = 0x7FFFFFFF  # 31-bit signed positive full-scale

        print(f"[ADC] Initialization complete. Channels: {self.channels}")

    def read_all_raw(self):
        try:
            return self.adc.ADS1263_GetAll(self.channels)
        except Exception as e:
            print(f"[ADC ERROR] read_all_raw failed: {e}")
            return [0] * len(self.channels)

    def raw_to_voltage(self, raw_value):
        # Handle signed conversion if needed
        if raw_value & 0x80000000:
            raw_value = raw_value - 0x100000000

        voltage = (raw_value / self.full_scale) * self.vref
        return voltage

    def read_channel_raw(self, channel: int):
        values = self.read_all_raw()

        if channel not in self.channels:
            raise ValueError(f"[ADC ERROR] Invalid channel: {channel}")

        idx = self.channels.index(channel)
        return int(values[idx])

    def read_channel_scaled(self, channel: int) -> float:
        raw_value = self.read_channel_raw(channel)
        adc_voltage = self.raw_to_voltage(raw_value)

        config = CHANNEL_SETTINGS[channel]
        scale = config.get("scale", 1.0)
        offset = config.get("offset", 0.0)

        return (adc_voltage * scale) + offset

    def read_named_channel(self, name: str) -> float:
        for ch, cfg in CHANNEL_SETTINGS.items():
            if cfg.get("name") == name:
                return self.read_channel_scaled(ch)

        raise ValueError(f"[ADC ERROR] No channel configured with name: {name}")

    def close(self):
        try:
            self.adc.ADS1263_Exit()
            print("[ADC] Shutdown complete.")
        except Exception:
            pass
