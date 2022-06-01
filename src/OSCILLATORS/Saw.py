from OSCILLATORS.Oscillator import Oscillator
import math
import numpy as np

class SawOscillator(Oscillator):
    def _post_freq_set(self):
        self._period = self._sample_rate / self._freq
        self._post_phase_set()

    def _post_phase_set(self):
        self._phase = ((self._phase + 90) / 360) * self._period

    def _init_osc(self):
        self._init = 0

    def __next__(self):
        div = (self._init + self._phase)/self._period
        out  = 2 * (div - math.floor(0.5 + div))
        self._init+=1
        if out not in range(*self._range):
            out = self.clip(out, *self._range)
        return out * self._amp

