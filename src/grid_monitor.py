from app_config.settings import (
    GRID_FAIL_THRESHOLD_ADC,
    GRID_RESTORE_THRESHOLD_ADC,
    GRID_RESTORE_FREQ_MIN,
    GRID_RESTORE_FREQ_MAX,
)


def read_grid_voltage(adc_reader) -> float:
    return adc_reader.read_named_channel("grid")


def is_grid_failed(adc_reader) -> bool:
    voltage = read_grid_voltage(adc_reader)
    return voltage < GRID_FAIL_THRESHOLD_ADC


def is_grid_restorable(adc_reader, grid_frequency_hz: float) -> bool:
    voltage = read_grid_voltage(adc_reader)

    voltage_ok = voltage > GRID_RESTORE_THRESHOLD_ADC
    frequency_ok = GRID_RESTORE_FREQ_MIN <= grid_frequency_hz <= GRID_RESTORE_FREQ_MAX

    return voltage_ok and frequency_ok
