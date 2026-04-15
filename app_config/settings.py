CHANNEL_SETTINGS = {
    0: {
        "name": "grid_voltage",
        "scale": 1.0,
        "offset": 0.0,
    },
    1: {
        "name": "grid_current",
        "scale": 1.0,
        "offset": 0.0,
    },
    3: {
        "name": "battery_voltage",
        "scale": 1.0,
        "offset": 0.0,
    },
    4: {
        "name": "battery_current",
        "scale": 1.0,
        "offset": 0.0,
    },
}

# Engineering thresholds
GRID_FAIL_VOLTAGE_AC = 100.0
GRID_RESTORE_VOLTAGE_AC = 110.0

GRID_RESTORE_FREQ_MIN = 59.0
GRID_RESTORE_FREQ_MAX = 61.0

# Bench-test ADC-equivalent thresholds
GRID_FAIL_THRESHOLD_ADC = 4.17
GRID_RESTORE_THRESHOLD_ADC = 4.58
BATTERY_LOW_THRESHOLD = 4.8

RELAY_GPIO = 17

# Timing and logging
POLL_INTERVAL = 0.5
LOG_FILE = "arpo_log.txt"
TRANSFER_DELAY = 1.5

# Planned inverter GPIOs
INVERTER_POS_GPIO = 23
INVERTER_NEG_GPIO = 24
