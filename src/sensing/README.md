# Sensing / Calibration Notes

This folder contains experimental and calibration-oriented ADC code that is not yet integrated into the live ARPO controller loop.

## Current contents
- `adc_rms_debug.py`:
  Captures a block of ADC samples, removes DC offset, computes RMS, and estimates mains RMS using a calibration constant.

## Why this is separate
The live ARPO controller currently uses simpler per-loop channel reads for mode detection and weekly integration testing.

The RMS/calibration approach is being kept separate until:
- analog buffering is finalized
- reference settings are confirmed
- integration timing is reviewed
- thresholds are updated to calibrated values

## Hardware notes from debugging
- ADC loading affected the analog node
- LM358 unity-gain buffering improved signal integrity
- common ground between converters mattered
- internal 2.5V reference needed to be used consistently

## Intended next step
Integrate calibrated RMS-based sensing into the controller after the weekly LCD/mode milestone is stable.
