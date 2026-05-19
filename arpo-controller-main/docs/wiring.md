# ARPO Wiring Notes

## ADS1263 High-Precision AD HAT
Mounted directly on Raspberry Pi GPIO header.

## Current channel plan
- AIN0 = Grid detection signal
- AIN1 = Battery voltage signal

## Relay
- BCM17 = Relay control signal

## Notes
- Never connect 120V AC directly to the Pi or ADC.
- Use isolation and safe scaling circuits for grid sensing.
- Use a voltage divider or approved sensor for battery voltage.
