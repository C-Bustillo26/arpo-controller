import RPi.GPIO as GPIO
import time

LEFT_IRL = 23      # left low-side N-MOSFET
RIGHT_IRL = 24     # change if your right IRL uses different GPIO

HALF_PERIOD = 0.0083   # ~60 Hz half-cycle
DEAD_TIME = 0.010      # 10 ms debug dead time

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_IRL, GPIO.OUT)
GPIO.setup(RIGHT_IRL, GPIO.OUT)

def all_off():
    GPIO.output(LEFT_IRL, GPIO.LOW)
    GPIO.output(RIGHT_IRL, GPIO.LOW)

try:
    print("Starting inverter debug test...")
    print(f"Dead time = {DEAD_TIME} seconds")

    all_off()
    time.sleep(1)

    while True:
        # Left side ON
        all_off()
        time.sleep(DEAD_TIME)
        GPIO.output(LEFT_IRL, GPIO.HIGH)
        time.sleep(HALF_PERIOD)

        # Dead time
        all_off()
        time.sleep(DEAD_TIME)

        # Right side ON
        GPIO.output(RIGHT_IRL, GPIO.HIGH)
        time.sleep(HALF_PERIOD)

except KeyboardInterrupt:
    print("Stopping inverter test...")

finally:
    all_off()
    GPIO.cleanup()
