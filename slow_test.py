import os
import time

while True:

    # ALL OFF
    os.system("pinctrl set 23 op dl")
    os.system("pinctrl set 24 op dl")
    print("ALL OFF")
    time.sleep(1)

    # DIAGONAL PAIR 1
    os.system("pinctrl set 23 op dh")
    print("GPIO 23 ON")
    time.sleep(1)

    # OFF
    os.system("pinctrl set 23 op dl")
    print("GPIO 23 OFF")
    time.sleep(1)

    # DIAGONAL PAIR 2
    os.system("pinctrl set 24 op dh")
    print("GPIO 24 ON")
    time.sleep(1)

    # OFF
    os.system("pinctrl set 24 op dl")
    print("GPIO 24 OFF")
    time.sleep(1)
