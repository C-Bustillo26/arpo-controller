import RPi.GPIO as GPIO
import time
from inverter_control import InverterController   # Change filename if needed

def main():
    print("=== Raspberry Pi H-Bridge Inverter Test ===\n")
    
    # Create the controller (change pins/frequency if your hardware is different)
    inverter = InverterController(
        pin1=23,      # Left High side
        pin2=24,      # Right High side
        frequency=20, # Start at 60 Hz
        dead_time=10e-6
    )

    print("Commands:")
    print("   start     - Start the inverter (square wave)")
    print("   stop      - Stop the inverter")
    print("   status    - Show current status")
    print("   freq X    - Change frequency to X Hz (e.g. freq 50)")
    print("   dead X    - Change dead time to X microseconds (e.g. dead 20)")
    print("   quit      - Exit the test\n")

    try:
        while True:
            cmd = input("> ").strip().lower()

            if cmd == "start":
                inverter.start()

            elif cmd == "stop":
                inverter.stop()

            elif cmd == "status":
                print(f"[Inverter] Status: {inverter.status()}")

            elif cmd.startswith("freq "):
                try:
                    new_freq = float(cmd.split()[1])
                    inverter.set_frequency(new_freq)
                except (IndexError, ValueError):
                    print("[Error] Usage: freq <value>  (e.g. freq 50)")

            elif cmd.startswith("dead "):
                try:
                    new_dead = float(cmd.split()[1])
                    inverter.set_dead_time(new_dead)
                except (IndexError, ValueError):
                    print("[Error] Usage: dead <value>  (e.g. dead 15)")

            elif cmd == "quit" or cmd == "q":
                print("[Test] Exiting...")
                inverter.stop()
                break

            else:
                print("Unknown command. Available: start, stop, status, freq X, dead X, quit")

    except KeyboardInterrupt:
        print("\n[Test] Interrupted by user (Ctrl+C)")
    finally:
        inverter.stop()
        GPIO.cleanup()          # Clean up all GPIO pins
        print("[Test] GPIO cleaned up. Test ended.")

if __name__ == "__main__":
    main()