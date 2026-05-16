# apro-controller-rev2

Integrated ARPO controller for Raspberry Pi hardware testing.

## Main updates

- Added RMS-based voltage and current sensing for IN0 through IN3.
- Added tested voltage and current calibration values in `app_config/settings.py`.
- Corrected DPDT relay polarity for GPIO 27.
- Runs the inverter square wave in a separate process to keep the GPIO timing stable during ADC, LCD, and relay operation.
- Uses full ADC reads in the main controller so terminal, LCD, and log current readings stay accurate.
- Adds timestamped run logs under `logs/`.
- Uses rotating 16x2 LCD pages for grid, backup, mode, and status.

## Hardware states

- GPIO 27 HIGH = grid/utility selected
- GPIO 27 LOW = backup/inverter selected
- GPIO 23 HIGH / GPIO 24 LOW = +12 V inverter polarity
- GPIO 23 LOW / GPIO 24 HIGH = -12 V inverter polarity
- GPIO 23 LOW / GPIO 24 LOW = inverter off
- GPIO 23 HIGH / GPIO 24 HIGH = unsafe and should not be commanded

## Run

```bash
cd /home/justin/Documents/apro-controller-rev2
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

Or run directly:

```bash
python3 -m src.main
```

## Important setting before final hardware testing

In `app_config/settings.py`, set:

```python
GPIO_LOGIC_TEST_IGNORE_BACKUP_LOW = False
```

when the inverter output and backup voltage sensing are connected and ready for protection testing.
