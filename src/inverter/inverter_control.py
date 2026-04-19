import RPi.GPIO as GPIO
import time

class InverterController:
    def __init__(self, pin1=23, pin2=24, frequency=60, dead_time=10e-6):
        self.pin1 = pin1   # Left High side
        self.pin2 = pin2   # Right High side
                
        self.frequency = frequency      # Default: 60 Hz
        self.dead_time = dead_time      # Default: 10 us
        self.running = False
        
        self._setup_gpio()
  
    def _setup_gpio(self):
        """Setup GPIO pins for H-bridge"""
        GPIO.setmode(GPIO.BCM)
        for pin in [self.pin1, self.pin2]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)  # Safe initial state

    def start(self):
        """Start generating 60 Hz square wave AC with dead time"""
        if not self.running:
            print(f"[Inverter] Starting inverter at {self.frequency} Hz "
                  f"(dead time: {self.dead_time*1e6:.1f} us)...")
            self.running = True
            self._generate_square_wave()

    def stop(self):
        """Stop the inverter safely"""
        if self.running:
            print("[Inverter] Stopping inverter...")
            self.running = False
        
        # All pins LOW = safe state
        for pin in [self.pin1, self.pin2]:
            GPIO.output(pin, 0)

    def status(self):
        """Return current inverter status"""
        return "ON" if self.running else "OFF"
        
    def _generate_square_wave(self):
        """Generate square wave at current frequency with dead time"""
        period = 1.0 / self.frequency
        half_period = period / 2

        print(f"[Inverter] Running at {self.frequency} Hz with {self.dead_time*1e6:.1f}us dead time")

        try:
            while self.running:
                # === Positive half-cycle ===
                GPIO.output(self.pin2, 0)
                time.sleep(self.dead_time)

                GPIO.output(self.pin1, 1)
                time.sleep(half_period - self.dead_time)

                #if not self.running:
                 #   break

                # === Dead time transition ===
                GPIO.output(self.pin1, 0)
                time.sleep(self.dead_time)

                # === Negative half-cycle ===
                GPIO.output(self.pin2, 1)
                time.sleep(half_period - self.dead_time)

               # if not self.running:
                   # break

                # === Dead time before next cycle ===
                GPIO.output(self.pin2, 0)
                time.sleep(self.dead_time)

        except KeyboardInterrupt:
            GPIO.output(self.pin1, 0)
            GPIO.output(self.pin2, 0)
            print("\n[Inverter] Interrupted by user")
        finally:
            self.stop()

    def set_frequency(self, new_freq):
        """Change frequency (takes effect after restart)"""
        if new_freq > 0:
            self.frequency = new_freq
            print(f"[Inverter] Frequency updated to {new_freq} Hz")

    def set_dead_time(self, new_dead_time_us):
        """Change dead time in microseconds"""
        new_dt = new_dead_time_us * 0.016
        if new_dt >= 0:
            self.dead_time = new_dt
            print(f"[Inverter] Dead time updated to {new_dead_time_us} us")