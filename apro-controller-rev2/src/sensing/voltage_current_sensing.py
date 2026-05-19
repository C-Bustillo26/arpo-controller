# ============================================================
# RMS voltage and current processing for ARPO ADC channels.
# ============================================================

import math


class VoltageCurrentSensing:

    # ============================================================
    # Converts raw ADS1263 samples into scaled voltage/current values.
    # ============================================================

    def __init__(self, adc, ref, sample_count, voltage_correction_a, voltage_correction_b):
        self.adc = adc
        self.ref = ref
        self.sample_count = sample_count
        self.voltage_correction_a = voltage_correction_a
        self.voltage_correction_b = voltage_correction_b

    def read_channel_samples(self, channel, sample_count=None):

	# ============================================================
	# Read multiple samples from one ADC channel.
	# ============================================================

        samples = []
        count = sample_count if sample_count is not None else self.sample_count

        for _ in range(count):
            raw = self.adc.ADS1263_GetChannalValue(channel)

            # ============================================================
            # Convert unsigned 32-bit ADC value to signed value when needed.
            # ============================================================

            if raw & 0x80000000:
                raw -= 0x100000000

            # ============================================================
            # Convert raw ADC counts to Pi-side voltage.
            # ============================================================

            voltage = raw * self.ref / 0x7FFFFFFF
            samples.append(voltage)

        return samples

    @staticmethod
    def rms_process(samples):

	# ============================================================
	# Remove DC offset and calculate AC RMS.
	# ============================================================

        mean = sum(samples) / len(samples)
        ac_samples = [sample - mean for sample in samples]
        rms = math.sqrt(sum(sample * sample for sample in ac_samples) / len(ac_samples))
        return mean, rms

    def process_voltage(self, channel, scale_factor, sample_count=None):

	# ============================================================
	# Return scaled RMS voltage for one ADC channel.
	# ============================================================

        samples = self.read_channel_samples(channel, sample_count=sample_count)

	# ============================================================
	# Voltage channels use a linear correction before RMS scaling.
	# ============================================================

        corrected_samples = [
            (self.voltage_correction_a * sample) + self.voltage_correction_b
            for sample in samples
        ]

        _, vrms = self.rms_process(corrected_samples)
        return scale_factor * vrms

    def process_current(self, channel, scale_factor):

	# ============================================================
	# Return scaled RMS current for one ADC channel.
	# ============================================================

        samples = self.read_channel_samples(channel)
        _, irms = self.rms_process(samples)
        return scale_factor * irms

    def process_current_debug(self, channel, scale_factor):

	# ============================================================
	# Return current channel diagnostic values for troubleshooting.
	# ============================================================

        samples = self.read_channel_samples(channel)
        mean, irms = self.rms_process(samples)
        return {
            "channel": channel,
            "min_v": min(samples),
            "max_v": max(samples),
            "mean_v": mean,
            "pi_irms_v": irms,
            "scale_factor": scale_factor,
            "final_a": scale_factor * irms,
        }
