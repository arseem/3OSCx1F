from abc import ABC, abstractmethod


class Oscillator(ABC):
    def __init__(self, freq, amp = 1, phase = 0, 
                    sample_rate=44100, range = (-1, 1), buff=256):
        self._init_freq = freq
        self._init_amp = amp
        self._init_phase = phase
        self._sample_rate = sample_rate
        self._range = range
        self._buff = buff

        self._freq = freq
        self._amp = amp
        self._phase = phase

        self.__iter__()

    @property
    def init_freq(self):
        return self._init_freq

    @property
    def init_phase(self):
        return self._init_phase

    @property
    def init_amp(self):
        return self._init_amp

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        self._freq = value
        self._post_freq_set()
    
    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value):
        self._phase = value
    
    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, value):
        self._amp = value

    def _post_freq_set(self):
        pass

    def _post_phase_set(self):
        pass

    def _post_amp_set(self):
        pass

    @staticmethod
    def clip(val, min_val=-1, max_val=1):
        return max_val if val>max_val else min_val if val<min_val else val

    @abstractmethod
    def _init_osc(self):
        pass

    @abstractmethod
    def __next__(self):
        return None

    def __iter__(self):
        self.freq = self._init_freq
        self.phase = self._init_phase
        self.amp = self._init_amp
        self._init_osc()
        return self
