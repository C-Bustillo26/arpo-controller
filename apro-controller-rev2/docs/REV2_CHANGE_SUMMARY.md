# Rev2 Change Summary

This revision keeps the repository structure but integrates the tested hardware paths.

## Controller integration

* Main controller is in `src/main.py`.
* Full ADC reads are used every loop so terminal output, LCD output, and logs show real current and voltage values.
* Timestamped run logs are created in `logs/`.
* Outage and restore timers are logged for report testing.

## ADC sensing

* ADS1263 sensing is handled through `src/adc\_reader.py` and `src/sensing/voltage\_current\_sensing.py`.
* Channel mapping is in `app\_config/settings.py`.
* Calibration constants are in `app\_config/settings.py` so they can be tuned by the team.
* `scripts/current\_channel\_debug.py` can be used to confirm current channels without running the full controller.

## Inverter GPIO timing

* Inverter waveform generation is handled by `src/inverter/inverter\_control.py`.
* The square wave runs in a separate process so ADC reads, LCD updates, and logging do not stretch the waveform timing.
* GPIO 23 and GPIO 24 are forced low during stop and cleanup.

## Relay logic

* DPDT relay control is handled by `src/relay\_control.py`.
* GPIO 27 HIGH selects grid/utility.
* GPIO 27 LOW selects backup/inverter.

## LCD

* The 16x2 LCD uses rotating pages for grid, backup, mode, and status.
* LCD output is handled by `src/display/lcd\_display.py` and `src/display/lcd\_driver.py`.

