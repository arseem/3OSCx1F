from dataclasses import dataclass
from random import sample
from re import X
from tkinter import Y
from xml.dom.expatbuilder import theDOMImplementation
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from OSCILLATORS.Sine import SineOscillator
from OSCILLATORS.Square import SquareOscillator
from OSCILLATORS.Triangle import TriangleOscillator
from OSCILLATORS.Saw import SawOscillator
from OSCILLATORS.Oscillator import Oscillator
import threading
from time import sleep


@dataclass
class Data:
    X = []
    Y = []
    I = 0
    LOCK = threading.Lock()

class Oscilloscope:

    def __init__(self, signal:Oscillator, size=255, ylow=None, yhigh=None):
        self.signal = signal
        self.amp = signal.amp
        self.freq = signal.freq
        self.fs = signal._sample_rate

        self.x = []
        self.y = []
        self.size = size
        self.ylow = ylow
        self.yhigh = yhigh
        self.timebase = 1/self.freq*self.fs

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ylow = ylow
        self.yhigh = yhigh
        self.ax.set_title(f'Signal waveform')
        self.ax.set_ylabel(f'Values')
        self.ax.set_xlabel('Time')
        self.ln, = self.ax.plot([], [])

        self.conf_thread = threading.Thread(target=self.init_plotting)


    def config_plot(self, title=None, ylabel=None, xlabel=None):
        if title:
            self.ax.set_title(f'{title}')
        if ylabel:
            self.ax.set_ylabel(f'{ylabel}')
        if xlabel:
            self.ax.set_xlabel(f'{xlabel}')


    def _tick(self, i):
        # self.y.append(next(self.signal))
        # self.x.append(i*(1/self.fs))
        with Data.LOCK:
            print('Reading Data')
            self.x = Data.X
            self.y = Data.Y

        self.ax.set_xlim(self.x[-self.size], self.x[-1]) if len(self.y)>self.size else plt.xlim(0, self.size*1/self.fs)
        self.ax.set_ylim(self.ylow, self.yhigh)

        self.ln.set_data(self.x, self.y)
        return self.ln,


    def init_plotting(self):
        self.ani = FuncAnimation(self.fig, self._tick, interval=self.timebase*1000/self.fs, blit=True)
        plt.show()


def generate_signal(signal, f, fs):
    while True:
        Data.I+=1
        with Data.LOCK:
            print('Adding Data')
            Data.Y.append(next(signal))
            Data.X.append(Data.I*1/fs)

        sleep(1/fs)


def main():
    f = 110
    a = 1
    fs = 1000
    size = 25
    signal = SquareOscillator(f, amp=a, sample_rate=fs)

    scope = Oscilloscope(signal, size=size, ylow=-1.1*a, yhigh=1.1*a)

    generation_thread = threading.Thread(target=generate_signal, args=(signal, f, fs))
    generation_thread.start()

    scope.init_plotting()


if __name__ == '__main__':
    main()