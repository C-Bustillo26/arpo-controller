# ============================================================
# ARPO controller settings.
# All hardware-specific values are kept here so everyone can tune their
# system without digging through the control logic.
# ============================================================

# ============================================================
# ADC DRIVER PATH
# ============================================================

# ============================================================
# Path used by the Waveshare ADS1263 example driver on the Raspberry Pi.
# ============================================================

ADC_DRIVER_PATH = "/home/justin/High-Pricision_AD_HAT/python"

# ============================================================
# Fallback path in case the folder was created with the corrected spelling.
# ============================================================

ADC_DRIVER_PATH_FALLBACK = "/home/justin/High-Precision_AD_HAT/python"


# ============================================================
# ADC SAMPLING SETTINGS
# ADC reference voltage used by the tested standalone sensing file.
# ============================================================

REF = 5.0

# ============================================================
# 20 samples at 1200 SPS is close to one 60 Hz cycle. This keeps the
# controller responsive while still using RMS instead of a single ADC sample.
# ============================================================

ADC_SAMPLE_COUNT = 20

# ============================================================
# ADS1263 sample rate. This must match a valid Waveshare ADS1263 rate string.
# ============================================================

ADC_RATE = "ADS1263_1200SPS"


# ============================================================
# ADC CHANNEL MAPPING
# Tested wiring:
# IN0 = grid voltage sense
# IN1 = grid current sense
# IN2 = backup/inverter voltage sense
# IN3 = backup/inverter current sense
# ============================================================

CHANNEL_SETTINGS = {
    0: {"name": "grid_voltage", "type": "voltage"},
    1: {"name": "grid_current", "type": "current"},
    2: {"name": "backup_voltage", "type": "voltage"},
    3: {"name": "backup_current", "type": "current"},
}


# ============================================================
# ADC CALIBRATION VALUES
# Voltage correction used before RMS scaling. These came from the tested
# standalone ADC file and correct the Pi-side voltage samples before applying
# the final VAC scale factor.
# ============================================================

A_V = 0.26682236
B_V = 1.76223583

# ============================================================
# Voltage scale factors. Increase or decrease these if the Pi voltage reading
# does not match a trusted meter. Example: if the Pi reads 115 VAC while the
# meter reads 120 VAC, multiply the existing factor by 120/115.
# ============================================================

K_GRID_V = 1055.5671
K_BACKUP_V = 1051.8716

# ============================================================
# Current scale factors. Increase or decrease these if the Pi current reading
# does not match a trusted clamp meter. Example: if the Pi reads 0.70 A while
# the meter reads 0.80 A, multiply the existing factor by 0.80/0.70.
# ============================================================

K_GRID_I = 2.9904
K_BACKUP_I = 3.19667


# ============================================================
# CONTROL THRESHOLDS
# ============================================================

GRID_FAIL_VOLTAGE_AC = 90.0
GRID_RESTORE_VOLTAGE_AC = 105.0
BACKUP_MIN_VOLTAGE_AC = 80.0
MAX_LOAD_CURRENT_A = 10.0


# ============================================================
# TIMING SETTINGS
# ============================================================

POLL_INTERVAL = 0.05
OUTAGE_CONFIRM_SECONDS = 0.25
RESTORE_CONFIRM_SECONDS = 0.50

# ============================================================
# Delay between inverter and relay commands. This is intentionally short, but
# should not be set to 0 while mechanical relays are being used.
# ============================================================

TRANSFER_DELAY = 0.20

# ============================================================
# Delay after inverter startup before validating backup voltage.
# ============================================================

BACKUP_STARTUP_GRACE_SECONDS = 0.10

# ============================================================
# Consecutive readings required before mode changes. This prevents one noisy
# ADC window from causing a transfer.
# ============================================================

GRID_LOW_COUNT_REQUIRED = 2
GRID_RESTORE_COUNT_REQUIRED = 2


# ============================================================
# GPIO SETTINGS
# ============================================================

RELAY_GPIO = 27

# ============================================================
# Tested relay module behavior:
# GPIO 27 HIGH = grid/utility position
# GPIO 27 LOW  = backup/inverter position
# ============================================================

RELAY_GRID_STATE = 1
RELAY_BACKUP_STATE = 0

# ============================================================
# Tested inverter polarity outputs:
# GPIO 23 HIGH / GPIO 24 LOW = +12 V
# GPIO 23 LOW  / GPIO 24 HIGH = -12 V
# GPIO 23 LOW  / GPIO 24 LOW = inverter off
# GPIO 23 HIGH / GPIO 24 HIGH = unsafe, never command this state
# ============================================================

INVERTER_POS_GPIO = 23
INVERTER_NEG_GPIO = 24


# ============================================================
# INVERTER SETTINGS
# The practical output frequency measured correctly with this setting in the
# integrated controller.
# ============================================================

INVERTER_FREQUENCY_HZ = 62.33

# ============================================================
# Dead time in microseconds. The inverter code converts this to seconds with
# dead_time_us * 1e-6.
# ============================================================

INVERTER_DEAD_TIME_US = 100


# ============================================================
# LCD SETTINGS
# ============================================================

LCD_I2C_ADDRESS = 0x27
LCD_COLUMNS = 16
LCD_ROWS = 2
LCD_PAGE_SECONDS = 2.0


# ============================================================
# LOGGING AND TEST SETTINGS
# ============================================================

LOG_FOLDER = "logs"

# ============================================================
# Set to None for real hardware. Set to "GRID", "BACKUP", or "FAULT" for
# software-only testing.
# ============================================================

TEST_MODE = None

# ============================================================
# Keep True during GPIO-only tests or when the inverter transformer is not
# connected. Set False before final protection testing so low backup voltage
# will create a FAULT.
# ============================================================

GPIO_LOGIC_TEST_IGNORE_BACKUP_LOW = True
