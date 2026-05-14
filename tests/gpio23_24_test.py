import RPi.GPIO as GPIO
import time

LEFT = 23
RIGHT = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LEFT, GPIO.OUT)
GPIO.setup(RIGHT, GPIO.OUT)

def both_off():
    GPIO.output(LEFT, GPIO.LOW)
    GPIO.output(RIGHT, GPIO.LOW)

try:
    print("Starting GPIO23/GPIO24 alternating test.")
    print("GPIO23 and GPIO24 should alternate every 1 second.")
    print("Press Ctrl+C to stop.")

    both_off()
    time.sleep(1)

    while True:
        print("GPIO23 HIGH, GPIO24 LOW")
        GPIO.output(LEFT, GPIO.HIGH)
        GPIO.output(RIGHT, GPIO.LOW)
        time.sleep(1)

        print("Both OFF dead-time")
        both_off()
        time.sleep(0.2)

        print("GPIO23 LOW, GPIO24 HIGH")
        GPIO.output(LEFT, GPIO.LOW)
        GPIO.output(RIGHT, GPIO.HIGH)
        time.sleep(1)

        print("Both OFF dead-time")
        both_off()
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopping test.")

finally:
    both_off()
    GPIO.cleanup()
    print("GPIO cleaned up. Both outputs OFF.")
