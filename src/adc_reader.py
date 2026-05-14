import math
import sys
from pathlib import Path

LIB_PATH = Path.home() / "High-Pricision_AD_HAT" / "python"

if not LIB_PATH.exists():
    raise FileNotFoundError(
        f"[ERROR] Waveshare ADC library not found at: {LIB_PATH}"
    )

sys.path.insert(0, str(LIB_PATH))

import ADS1263  # type: ignore
from app_config.settings import CHANNEL_SETTINGS


class ADCReader:
    def __init__(self):
        print("[ADC] Initializing ADS1263...")

        self.adc = ADS1263.ADS1263()

        if self.adc.ADS1263_init_ADC1("ADS1263_400SPS") == -1:
            raise RuntimeError("[ADC] Initialization failed!")

        self.adc.ADS1263_SetMode(0)

        self.channels = sorted(CHANNEL_SETTINGS.keys())

        self.ref = 2.5
        self.full_scale = 0x7FFFFFFF
        self.default_samples = 1000

        print(f"[ADC] Initialization complete. Channels: {self.channels}")

    def raw_to_voltage(self, raw_value):
        if raw_value & 0x80000000:
            raw_value = raw_value - 0x100000000

        return raw_value * self.ref / self.full_scale

    def read_channel_raw(self, channel: int):
        if channel not in self.channels:
            raise ValueError(f"[ADC ERROR] Invalid channel: {channel}")

        return self.adc.ADS1263_GetChannalValue(channel)

    def read_channel_voltage(self, channel: int) -> float:
        raw_value = self.read_channel_raw(channel)
        return self.raw_to_voltage(raw_value)

    def capture_voltage_rms(self, channel: int, samples_count=None) -> dict:
        if samples_count is None:
            samples_count = self.default_samples

        samples = []

        for _ in range(samples_count):
            raw = self.read_channel_raw(channel)
            voltage = self.raw_to_voltage(raw)
            samples.append(voltage)

        mean = sum(samples) / len(samples)
        ac = [x - mean for x in samples]
        vrms_pi = math.sqrt(sum(x * x for x in ac) / len(ac))

        return {
            "dc_offset": mean,
            "vrms_pi": vrms_pi,
        }

    def read_channel_scaled(self, channel: int) -> float:
        config = CHANNEL_SETTINGS[channel]
        name = config.get("name", "")
        scale = config.get("scale", 1.0)
        offset = config.get("offset", 0.0)
        measurement_type = config.get("type", "dc")

        if measurement_type == "ac_rms":
            rms_data = self.capture_voltage_rms(channel)
            return (rms_data["vrms_pi"] * scale) + offset

        voltage = self.read_channel_voltage(channel)
        return (voltage * scale) + offset

    def read_named_channel(self, name: str) -> float:
        for channel, config in CHANNEL_SETTINGS.items():
            if config.get("name") == name:
                return self.read_channel_scaled(channel)

        raise ValueError(f"[ADC ERROR] No channel configured with name: {name}")

    def close(self):
        try:
            self.adc.ADS1263_Exit()
            print("[ADC] Shutdown complete.")
        except Exception:
            pass
