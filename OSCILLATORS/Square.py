from OSCILLATORS.Sine import SineOscillator
import math

class SquareOscillator(SineOscillator):
    def __init__(self, freq, amp = 1, phase = 0, 
                    sample_rate=44100, range = (-1, 1), threshold = 0):
        super().__init__(freq, amp, phase, sample_rate, range)
        self._threshold = threshold

    def __next__(self):
        out = math.sin(self._init + self._phase)
        self._init+=self._step
        out = self._range[1] if out > self._threshold else self._range[0]
        
        return out * self._amp if self._amp!=1 else out * 0.999