from app_config.settings import GRID_ON_THRESHOLD


def is_grid_on(adc_reader) -> bool:
    voltage = adc_reader.read_named_channel("grid")
    return voltage > GRID_ON_THRESHOLD


def read_grid_voltage(adc_reader) -> float:
    return adc_reader.read_named_channel("grid")
