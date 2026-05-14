import RPi.GPIO as GPIO
import time

LEFT = 23
RIGHT = 24

ON_TIME = 0.1       # 100 ms
DEAD_TIME = 0.05    # 50 ms

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LEFT, GPIO.OUT)
GPIO.setup(RIGHT, GPIO.OUT)

def both_off():
    GPIO.output(LEFT, GPIO.LOW)
    GPIO.output(RIGHT, GPIO.LOW)

try:
    print("Starting SAFE slow inverter test")
    print("GPIO23/GPIO24 alternate with 50 ms dead-time")
    print("Press Ctrl+C to stop")

    both_off()
    time.sleep(1)

    while True:
        # Left side ON
        GPIO.output(LEFT, GPIO.HIGH)
        GPIO.output(RIGHT, GPIO.LOW)
        time.sleep(ON_TIME)

        # Dead-time: both OFF
        both_off()
        time.sleep(DEAD_TIME)

        # Right side ON
        GPIO.output(LEFT, GPIO.LOW)
        GPIO.output(RIGHT, GPIO.HIGH)
        time.sleep(ON_TIME)

        # Dead-time: both OFF
        both_off()
        time.sleep(DEAD_TIME)

except KeyboardInterrupt:
    print("\nStopping test")

finally:
    both_off()
    GPIO.cleanup()
    print("GPIO cleaned up. Both outputs OFF.")
