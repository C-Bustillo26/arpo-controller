import os
import time

GPIO_A = 23  # left FQP + right IRL
GPIO_B = 24  # right FQP + left IRL

half_cycle = 1 / 120      # 8.33 ms for 60 Hz output
dead_time = 0.0005        # 0.5 ms

while True:
    os.system(f"pinctrl set {GPIO_A} op dl")
    os.system(f"pinctrl set {GPIO_B} op dl")
    time.sleep(dead_time)

    os.system(f"pinctrl set {GPIO_A} op dh")
    time.sleep(half_cycle - dead_time)

    os.system(f"pinctrl set {GPIO_A} op dl")
    os.system(f"pinctrl set {GPIO_B} op dl")
    time.sleep(dead_time)

    os.system(f"pinctrl set {GPIO_B} op dh")
    time.sleep(half_cycle - dead_time)
