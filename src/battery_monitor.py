from app_config.settings import BATTERY_LOW_THRESHOLD


def read_battery_voltage(adc_reader) -> float:
    return adc_reader.read_named_channel("battery")


def is_battery_low(adc_reader) -> bool:
    voltage = read_battery_voltage(adc_reader)
    return voltage < BATTERY_LOW_THRESHOLD
