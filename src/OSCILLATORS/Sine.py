from OSCILLATORS.Oscillator import Oscillator
import math

class SineOscillator(Oscillator):
    def _post_freq_set(self):
        self._step = (2*math.pi*self._freq)/self._sample_rate

    def _post_phase_set(self):
        self._phase = (self._phase / 360) * math.pi * 2

    def _init_osc(self):
        self._init = 0
    
    def __next__(self):
        out = math.sin(self._init + self._phase)
        self._init+=self._step
        if out not in range(*self._range):
            out = self.clip(out, *self._range)
        
        return out * self._amp