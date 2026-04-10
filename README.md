# ARPO Controller

ARPO (Automated Reflex to Power Outage) controller for Raspberry Pi using the Waveshare High-Pricision AD HAT.

## Features
- Reads grid voltage
- Reads battery voltage
- Detects grid outage
- Controls relay switching between grid and backup

## Folder Structure
- `config/` adjustable settings
- `src/` source code
- `docs/` wiring notes

## Setup
```bash
git clone <your-repo-url>
cd arpo-controller
chmod +x setup.sh run.sh
./setup.sh
./run.sh
