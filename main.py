from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['toolbar'] = 'None'
from matplotlib.animation import FuncAnimation
from OSCILLATORS.Sine import SineOscillator
from OSCILLATORS.Square import SquareOscillator
from OSCILLATORS.Triangle import TriangleOscillator
from OSCILLATORS.Saw import SawOscillator
from OSCILLATORS.Oscillator import Oscillator
import threading
from time import sleep, perf_counter
from scipy.fft import rfftfreq, rfft


@dataclass
class Appearance:
    color_bg = '#0F110D'
    color_front = '#FFFF21'
    color_font = 'white'
    color_add = 'red'

@dataclass
class Data:
    X = []
    Y = []
    I = 0
    LOCK = threading.Lock()

class Oscilloscope:

    def __init__(self, signal:Oscillator, ylow=None, yhigh=None):
        self.signal = signal
        self.amp = signal.amp
        self.freq = signal.freq
        self.fs = signal._sample_rate

        self.x = []
        self.y = []
        self.size = int(1/self.freq*self.fs*3)
        self.ylow = ylow
        self.yhigh = yhigh
        self.timebase = 6000
        self.ylow = ylow
        self.yhigh = yhigh

        self.fig = plt.figure(facecolor=Appearance.color_bg)

        #--------------------WAVEFORM PLOT CUSTOMIZATON-------------------

        self.ax = self.fig.add_subplot(2, 1, 1)
        self.ax.set_title(f'Signal waveform', color=Appearance.color_font)
        self.ax.set_ylabel(f'Values', color=Appearance.color_font)
        self.ax.set_xlabel('Time', color=Appearance.color_font)
        self.ax.set_facecolor(Appearance.color_bg)
        self.ax.spines['bottom'].set_color(Appearance.color_font)
        self.ax.spines['top'].set_color(Appearance.color_font)
        self.ax.spines['left'].set_color(Appearance.color_font)
        self.ax.spines['right'].set_color(Appearance.color_font)
        self.ax.xaxis.label.set_color(Appearance.color_font)
        self.ax.yaxis.label.set_color(Appearance.color_font)
        self.ax.tick_params(axis='x', colors=Appearance.color_font)
        self.ax.tick_params(axis='y', colors=Appearance.color_font)
        self.ln, = self.ax.plot([], [], color=Appearance.color_front)

        #--------------------SPECTRUM PLOT CUSTOMIZATON-------------------

        self.axf = self.fig.add_subplot(2, 1, 2)
        self.axf.set_xscale('log')
        self.axf.set_title(f'Signal spectrum', color=Appearance.color_font)
        self.axf.set_ylabel(f'Values', color=Appearance.color_font)
        self.axf.set_xlabel('Frequency', color=Appearance.color_font)
        self.axf.set_facecolor(Appearance.color_bg)
        self.axf.spines['bottom'].set_color(Appearance.color_font)
        self.axf.spines['top'].set_color(Appearance.color_font)
        self.axf.spines['left'].set_color(Appearance.color_font)
        self.axf.spines['right'].set_color(Appearance.color_font)
        self.axf.xaxis.label.set_color(Appearance.color_font)
        self.axf.yaxis.label.set_color(Appearance.color_font)
        self.axf.tick_params(axis='x', colors=Appearance.color_font)
        self.axf.tick_params(axis='y', colors=Appearance.color_font)
        self.lnf, = self.axf.plot([], [], color=Appearance.color_front)
        self.lnf_filt, = self.axf.plot([], [], color=Appearance.color_add)

        plt.tight_layout()


    def config_plot(self, title=None, ylabel=None, xlabel=None):
        if title:
            self.ax.set_title(f'{title}')
        if ylabel:
            self.ax.set_ylabel(f'{ylabel}')
        if xlabel:
            self.ax.set_xlabel(f'{xlabel}')


    def _tick(self, i):
        with Data.LOCK:
            #print('Reading Data')
            self.x = Data.X
            self.y = Data.Y

        self.ax.set_xlim(self.x[-self.size], self.x[-1]) if len(self.y)>self.size else self.ax.set_xlim(0, self.size*1/self.fs)
        self.ax.set_ylim(self.ylow, self.yhigh)
        if i%(500)==0:
            self.ax.figure.canvas.draw()

        self.ln.set_data(self.x[-self.size:], self.y[-self.size:])

        if len(self.y)<self.size:
            self.axf.set_ylim(0, 40)
            self.axf.set_xlim(0, self.fs/2)
            return self.ln, 

        else:
            xf = rfftfreq(self.size, 1/self.fs)
            yf = rfft(self.y[-self.size:])
            yf_scale = 20*np.log10(np.abs(yf))
            self.lnf.set_data(xf, -max(yf_scale)+yf_scale)
            self.axf.set_ylim(min(-max(yf_scale)+yf_scale)*1.1, 0)
            self.axf.set_xlim(0, self.fs/2)
            return self.ln, self.lnf, 


    def init_plotting(self):
        self.ani = FuncAnimation(self.fig, self._tick, interval=self.timebase/1000, blit=True)
        plt.show()


def generate_signal(signal, f, fs):
    while True:
        start = perf_counter()
        Data.I+=1
        with Data.LOCK:
            #print('Adding Data')
            Data.Y.append(next(signal))
            Data.X.append(Data.I*1/fs)

        #sleep(1/fs)
        while perf_counter()-start < 1/fs:
            print(f'{Data.I}\t:\t{perf_counter()-start} < {1/fs}\t:\twaiting')


def main():
    f = 20
    a = 1
    fs = 1000
    signal = SineOscillator(f, amp=a, sample_rate=fs)

    scope = Oscilloscope(signal, ylow=-1.1*a, yhigh=1.1*a)

    generation_thread = threading.Thread(target=generate_signal, args=(signal, f, fs))
    generation_thread.start()

    scope.init_plotting()


if __name__ == '__main__':
    main()