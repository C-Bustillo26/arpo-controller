CHANNEL_SETTINGS = {
    0: {
        "name": "grid_voltage",
        "type": "ac_rms",
        "scale": 291.9112,
        "offset": 0.0,
    },
    1: {
        "name": "grid_current",
        "type": "dc",
        "scale": 1.0,
        "offset": 0.0,
    },
    3: {
        "name": "battery_voltage",
        "type": "dc",
        "scale": 1.0,
        "offset": 0.0,
    },
    4: {
        "name": "battery_current",
        "type": "dc",
        "scale": 1.0,
        "offset": 0.0,
    },
}

# =========================
# Grid Thresholds
# =========================

# Real AC RMS thresholds
GRID_FAIL_THRESHOLD_ADC = 100.0
GRID_RESTORE_THRESHOLD_ADC = 110.0

# Frequency thresholds for grid restoration
GRID_RESTORE_FREQ_MIN = 59.0
GRID_RESTORE_FREQ_MAX = 61.0

# Battery protection threshold
BATTERY_LOW_THRESHOLD = 4.8

# =========================
# GPIO Configuration
# =========================

RELAY_GPIO = 27

INVERTER_POS_GPIO = 23
INVERTER_NEG_GPIO = 24

# =========================
# Timing / Logging
# =========================

POLL_INTERVAL = 0.5

TRANSFER_DELAY = 1.5

LOG_FILE = "arpo_log.txt"
