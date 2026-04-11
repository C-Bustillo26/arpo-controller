# ARPO Controller

# ARPO Controller (Automated Reflex to Power Outage)

## Overview
ARPO is a Raspberry Pi–based system designed to automatically detect grid power loss and safely transfer a load to a backup power source. The system also manages the return to grid power when conditions are stable.

---

## Current Features
- ADC-based voltage sensing (grid and battery)
- Grid failure detection using voltage threshold
- Grid restore logic using:
  - Voltage threshold (hysteresis)
  - Frequency check (placeholder)
- Safe relay switching with transfer delay (< 2 seconds)
- Inverter control module integration
- Real-time logging of system behavior

---

## System Architecture

---

## Safety Logic
- Grid fail threshold and restore threshold are separated to prevent oscillation
- Frequency must be within acceptable range before returning to grid
- Relay and inverter switching is sequenced with delay to prevent unsafe transitions

---

## Hardware Context
- Load: ~100 W
- Backup system: 12 V battery + inverter
- Grid: 120 VAC
- ADC used for voltage sensing (scaled input)

---

## Team Roles
- **Cel (you):**
  - Software architecture
  - ADC integration
  - Grid detection logic
  - High-voltage system collaboration

- **Teammate 1:**
  - Inverter design and implementation

- **Teammate 2:**
  - High-voltage switching / power stage

---

## Running the Project

```bash
cd ~/arpo-controller
./run.sh
