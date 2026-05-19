# ============================================================
# Process-based inverter H-bridge GPIO control.
# ============================================================

import multiprocessing
import time

import RPi.GPIO as GPIO

from app_config.settings import (
    INVERTER_POS_GPIO,
    INVERTER_NEG_GPIO,
    INVERTER_FREQUENCY_HZ,
    INVERTER_DEAD_TIME_US,
)


def _safe_all_off(pin1, pin2):

    # ============================================================
    # Force both inverter GPIO outputs low.
    # ============================================================

    GPIO.output(pin1, GPIO.LOW)
    GPIO.output(pin2, GPIO.LOW)


def _inverter_process_loop(pin1, pin2, frequency, dead_time_seconds, stop_event):

    # ============================================================
    # Generate the inverter square wave in a separate process.
    # ============================================================

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin1, GPIO.OUT)
    GPIO.setup(pin2, GPIO.OUT)

    _safe_all_off(pin1, pin2)

    period = 1.0 / frequency
    half_period = period / 2.0

    if dead_time_seconds >= half_period:
        _safe_all_off(pin1, pin2)
        raise ValueError("[Inverter] Dead time is too large for selected frequency.")

    on_time = half_period - dead_time_seconds

    print(
        f"[Inverter Process] Running at {frequency} Hz "
        f"with {dead_time_seconds * 1e6:.1f} us dead time"
    )

    try:
        while not stop_event.is_set():

            # ============================================================
            # Positive half-cycle. Hardware result:
            # GPIO 23 HIGH and GPIO 24 LOW.
            # ============================================================

            GPIO.output(pin2, GPIO.LOW)
            time.sleep(dead_time_seconds)
            GPIO.output(pin1, GPIO.HIGH)
            time.sleep(on_time)

            # ============================================================
            # Dead-time state between polarity changes.
            # Both outputs must be low.
            # ============================================================

            GPIO.output(pin1, GPIO.LOW)
            GPIO.output(pin2, GPIO.LOW)
            time.sleep(dead_time_seconds)

            # ============================================================
            # Negative half-cycle. Hardware result:
            # GPIO 23 LOW and GPIO 24 HIGH.
            # ============================================================

            GPIO.output(pin1, GPIO.LOW)
            time.sleep(dead_time_seconds)
            GPIO.output(pin2, GPIO.HIGH)
            time.sleep(on_time)

            # ============================================================
            # Dead-time state before repeating.
            # ============================================================

            GPIO.output(pin1, GPIO.LOW)
            GPIO.output(pin2, GPIO.LOW)
            time.sleep(dead_time_seconds)

    finally:
        _safe_all_off(pin1, pin2)
        print("[Inverter Process] GPIO outputs forced OFF")


class InverterController:

    # ============================================================
    # Starts and stops the inverter waveform process.
    # ============================================================

    def __init__(
        self,
        pin1=INVERTER_POS_GPIO,
        pin2=INVERTER_NEG_GPIO,
        frequency=INVERTER_FREQUENCY_HZ,
        dead_time_us=INVERTER_DEAD_TIME_US,
    ):
        self.pin1 = pin1
        self.pin2 = pin2
        self.frequency = frequency

        # ============================================================
        # Convert microseconds from settings.py into seconds
        # for time.sleep().
        # ============================================================

        self.dead_time = dead_time_us * 1e-6

        self._stop_event = None
        self._process = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin1, GPIO.OUT)
        GPIO.setup(self.pin2, GPIO.OUT)

        self._all_off()

        print("[Inverter] On standby. Process-based waveform enabled.")

    def _all_off(self):

        # ============================================================
        # Force the inverter output GPIOs to the safe OFF state.
        # ============================================================

        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)

    def start(self):

        # ============================================================
        # Start the inverter waveform if it is not already running.
        # ============================================================

        if self._process is not None and self._process.is_alive():
            return

        self._stop_event = multiprocessing.Event()

        self._process = multiprocessing.Process(
            target=_inverter_process_loop,
            args=(
                self.pin1,
                self.pin2,
                self.frequency,
                self.dead_time,
                self._stop_event,
            ),
            daemon=True,
        )

        self._process.start()

        print("[Inverter] Square wave process started")

    def stop(self):

        # ============================================================
        # Stop the inverter waveform and force both GPIOs low.
        # ============================================================

        if self._stop_event is not None:
            self._stop_event.set()

        if self._process is not None and self._process.is_alive():
            self._process.join(timeout=1.0)

            if self._process.is_alive():
                print("[Inverter] Process did not stop cleanly. Terminating.")
                self._process.terminate()
                self._process.join(timeout=1.0)

        self._process = None
        self._stop_event = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.pin1, GPIO.OUT)
        GPIO.setup(self.pin2, GPIO.OUT)

        self._all_off()

        print("[Inverter] Square wave stopped and GPIO forced OFF")

    def status(self):

        # ============================================================
        # Return ON or OFF for LCD and log output.
        # ============================================================

        if self._process is not None and self._process.is_alive():
            return "ON"

        return "OFF"

    def set_frequency(self, new_freq):

        # ============================================================
        # Update frequency.
        # Stop and restart inverter for change to apply.
        # ============================================================

        if new_freq <= 0:
            raise ValueError("[Inverter] Frequency must be greater than 0.")

        self.frequency = new_freq

        print(f"[Inverter] Frequency updated to {new_freq} Hz")

    def set_dead_time(self, new_dead_time_us):

        # ============================================================
        # Update dead time in microseconds.
        # ============================================================

        if new_dead_time_us < 0:
            raise ValueError("[Inverter] Dead time cannot be negative.")

        self.dead_time = new_dead_time_us * 1e-6

        print(f"[Inverter] Dead time updated to {new_dead_time_us} us")