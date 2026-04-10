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

GRID_ON_THRESHOLD = 0.20
BATTERY_LOW_THRESHOLD = 4.8

RELAY_GPIO = 17
POLL_INTERVAL = 1.0
