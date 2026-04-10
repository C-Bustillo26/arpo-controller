# Channel configuration
# scale and offset let you convert ADC voltage into real-world values

CHANNEL_SETTINGS = {
    0: {
        "name": "grid",
        "scale": 1.0,
        "offset": 0.0,
    },
    1: {
        "name": "battery",
        "scale": 1.0,
        "offset": 0.0,
    },
}

# Actual engineering thresholds
GRID_FAIL_VOLTAGE_AC = 100.0
GRID_RESTORE_VOLTAGE_AC = 110.0

GRID_RESTORE_FREQ_MIN = 59.0
GRID_RESTORE_FREQ_MAX = 61.0

BATTERY_LOW_THRESHOLD = 4.8

# Current bench-test ADC equivalents
# Assumes about 5.0 V ADC reading corresponds to healthy nominal grid
GRID_FAIL_THRESHOLD_ADC = 4.17
GRID_RESTORE_THRESHOLD_ADC = 4.58

RELAY_GPIO = 17
POLL_INTERVAL = 0.5
LOG_FILE = "arpo_log.txt"

# Must stay under engineering requirement of 2 seconds
TRANSFER_DELAY = 1.5
