from OSCILLATORS.Saw import SawOscillator
import math

class TriangleOscillator(SawOscillator):
    def __next__(self):
        div = (self._init + self._phase)/self._period
        out = 2 * (div - math.floor(0.5 + div))
        out = (abs(out) - 0.5) * 2
        self._init+=1
        if out not in range(*self._range):
            out = self.clip(out, *self._range)
        return out * self._amp