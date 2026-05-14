import RPi.GPIO as GPIO
import time
import threading


class InverterController:
    def __init__(self, pin1=23, pin2=24, frequency=62.33, dead_time=10e-5):
        self.pin1 = pin1
        self.pin2 = pin2

        self.frequency = frequency
        self.dead_time = dead_time
        self.running = False
        self._wave_thread = None

        print("[Inverter] On standby.")
        self._setup_gpio()

    def _setup_gpio(self):
        """Set up GPIO pins for the inverter H-bridge."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in [self.pin1, self.pin2]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        print(f"[Inverter] GPIO initialized on pins {self.pin1} and {self.pin2}")

    def start(self):
        """Start generating the inverter square wave in a background thread."""
        if self.running:
            return

        self.running = True

        self._wave_thread = threading.Thread(
            target=self._generate_square_wave,
            daemon=True,
            name="InverterWave"
        )

        self._wave_thread.start()
        print("[Inverter] Square wave started in background thread")

    def stop(self):
        """Stop the inverter safely."""
        if not self.running:
            GPIO.output(self.pin1, GPIO.LOW)
            GPIO.output(self.pin2, GPIO.LOW)
            return

        self.running = False

        if (
            self._wave_thread
            and self._wave_thread.is_alive()
            and threading.current_thread() != self._wave_thread
        ):
            self._wave_thread.join(timeout=0.2)

        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)

        print("[Inverter] Square wave stopped")

    def status(self):
        """Return current inverter status."""
        return "ON" if self.running else "OFF"

    def _generate_square_wave(self):
        """Generate square wave at the selected frequency with dead time."""
        period = 1.0 / self.frequency
        half_period = period / 2.0
        on_time = half_period - self.dead_time

        if on_time <= 0:
            print("[Inverter ERROR] Dead time is too large for selected frequency.")
            self.running = False
            GPIO.output(self.pin1, GPIO.LOW)
            GPIO.output(self.pin2, GPIO.LOW)
            return

        print(
            f"[Inverter] Running at {self.frequency} Hz "
            f"with {self.dead_time * 1e6:.1f} us dead time"
        )

        try:
            while self.running:
                # Positive half-cycle
                GPIO.output(self.pin2, GPIO.LOW)
                time.sleep(self.dead_time)

                GPIO.output(self.pin1, GPIO.HIGH)
                time.sleep(on_time)

                # Dead time transition
                GPIO.output(self.pin1, GPIO.LOW)
                time.sleep(self.dead_time)

                # Negative half-cycle
                GPIO.output(self.pin2, GPIO.HIGH)
                time.sleep(on_time)

                # Dead time before next cycle
                GPIO.output(self.pin2, GPIO.LOW)
                time.sleep(self.dead_time)

        except KeyboardInterrupt:
            print("\n[Inverter] Interrupted by user")

        except Exception as e:
            print(f"[Inverter ERROR] {e}")

        finally:
            GPIO.output(self.pin1, GPIO.LOW)
            GPIO.output(self.pin2, GPIO.LOW)
            self.running = False
            print("[Inverter] Output pins forced LOW")

    def set_frequency(self, new_freq):
        """Change inverter frequency."""
        if new_freq <= 0:
            print("[Inverter ERROR] Frequency must be greater than 0")
            return

        self.frequency = new_freq
        print(f"[Inverter] Frequency updated to {new_freq} Hz")

    def set_dead_time(self, new_dead_time_us):
        """Change dead time using microseconds."""
        if new_dead_time_us < 0:
            print("[Inverter ERROR] Dead time cannot be negative")
            return

        self.dead_time = new_dead_time_us / 1_000_000.0
        print(f"[Inverter] Dead time updated to {new_dead_time_us} us")

    def cleanup(self):
        """Clean inverter outputs."""
        self.stop()
        print("[Inverter] Cleanup complete")
