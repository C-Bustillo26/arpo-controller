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

REF = 2.5
N = 1000
K_V = 291.9112


def capture_voltage_rms(channel=0, samples_count=N):
    adc = ADS1263.ADS1263()

    if adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1:
        raise RuntimeError("ADC init failed")

    adc.ADS1263_SetMode(0)

    samples = []

    print("Collecting samples...")

    for _ in range(samples_count):
        raw = adc.ADS1263_GetChannalValue(channel)
        v = raw * REF / 0x7fffffff
        samples.append(v)

    mean = sum(samples) / len(samples)
    ac = [x - mean for x in samples]
    vrms_pi = math.sqrt(sum(x * x for x in ac) / len(ac))
    vrms_mains = K_V * vrms_pi

    print(f"\nDC Offset = {mean:.6f} V")
    print(f"Pi Measured Vrms = {vrms_pi:.6f} V")
    print(f"Estimated Mains Vrms = {vrms_mains:.3f} VAC")

    try:
        adc.ADS1263_Exit()
    except Exception:
        pass

    return {
        "dc_offset": mean,
        "vrms_pi": vrms_pi,
        "vrms_mains": vrms_mains,
    }


if __name__ == "__main__":
    capture_voltage_rms()
