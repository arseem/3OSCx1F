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
from scipy.signal import butter, sosfilt, sosfilt_zi, sosfreqz


@dataclass
class Appearance:
    color_bg = '#0F110D'
    color_front = '#FFFF21'
    color_font = 'white'
    color_add = 'red'
    color_back = 'gray'

@dataclass
class Global_data:
    fs = 1000


@dataclass
class Config:
    freq = 5
    amp = 1

    filter_type = 0
    cutoff = 10
    order = 24

    length = int(1/freq*Global_data.fs*3)
    timebase = length/Global_data.fs
    

@dataclass
class Data:
    X = []
    Y = []
    Ytf = []
    I = 0
    LOCK = threading.Lock()


@dataclass
class Generators:
    signals = []
    filters = []
    filters_zi = []
    filters_freqz = []

class Oscilloscope:

    def __init__(self, ylow=None, yhigh=None):
        self.freq = Generators.signals[0].freq
        self.fs = Global_data.fs

        self.x = []
        self.y = []
        self.size = Config.length
        self.ylow = ylow
        self.yhigh = yhigh
        self.timebase = Config.timebase
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
        self.ln_pre, = self.ax.plot([], [], color=Appearance.color_back, alpha=0.1)

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
            self.y_pre = Data.Ytf

        self.ax.set_xlim(self.x[-self.size], self.x[-1]) if len(self.y)>self.size else self.ax.set_xlim(0, self.size*1/self.fs)
        self.ax.set_ylim(self.ylow, self.yhigh)

        self.ln.set_data(self.x[-self.size:], self.y[-self.size:])
        self.ln_pre.set_data(self.x[-self.size:], self.y_pre[-self.size:])

        if len(self.y)<self.size:
            self.axf.set_ylim(-40, 0)
            self.axf.set_xlim(0, self.fs/2)
            return self.ln, 

        else:
            xf = rfftfreq(self.size, 1/self.fs)
            yf = rfft(self.y[-self.size:])
            w = Generators.filters_freqz[0][0]
            h = Generators.filters_freqz[0][1]
            yf_scale = 20*np.log10(np.abs(yf))
            self.lnf.set_data(xf, -max(yf_scale)+yf_scale)
            fill = self.axf.fill_between(xf, -max(yf_scale)+yf_scale, min(-max(yf_scale)+yf_scale), color=Appearance.color_front)
            self.axf.set_ylim(min(-max(yf_scale)+yf_scale)*1.1, 0)
            self.axf.set_xlim(0, self.fs/2)
            self.lnf_filt.set_data(w/2/3.14*self.fs, 20*np.log10(abs(h)))
        
        if i%(500)==0:
            self.ax.figure.canvas.draw()
            self.axf.figure.canvas.draw()

        return self.ln, self.lnf, fill, self.ln_pre, self.lnf_filt, 


    def init_plotting(self):
        self.ani = FuncAnimation(self.fig, self._tick, interval=self.timebase*1000, blit=True)
        plt.show()


def generate_signal():
    while True:
        start = perf_counter()
        Data.I+=1
        # with Data.LOCK:
        #     #print('Adding Data')
        #     Data.Y.append(next(Generators.signals[0]))
        #     Data.X.append(Data.I*1/Global_data.fs)
        Data.Ytf.append(next(Generators.signals[0]))

        with Data.LOCK:
            Data.X.append(Data.I*1/Global_data.fs)
            filter_signal()

        #sleep(1/fs)
        end = perf_counter()
        while end-start < 1/Global_data.fs/2:
            print(f'---{Data.I}\t:\t{end-start} < {1/Global_data.fs}\t:\tWAITING {end-start-1/Global_data.fs}s---')
            end = perf_counter()

        print(f'---{Data.I}\t:\tNEXT ITERATION---')


def filter_signal():
    delay = Global_data.fs//2*10
    if len(Data.Ytf) <= delay:
        Data.Y = (list(sosfilt(Generators.filters[0], Data.Ytf, zi=Generators.filters_zi[0]*Data.Ytf[0]))[0])
    else:
        Data.Y[-delay:] = (list(sosfilt(Generators.filters[0], Data.Ytf[-delay:], zi=Generators.filters_zi[0]*Data.Ytf[-delay]))[0])



def main():
    Generators.signals.append(SawOscillator(Config.freq, amp=Config.amp, sample_rate=Global_data.fs))

    order = 24
    cutoff = 5
    sos = butter(order, cutoff*2/Global_data.fs, output = 'sos', btype='lowpass')
    w, h = sosfreqz(sos)
    Generators.filters.append(sos)
    Generators.filters_freqz.append((w, h))
    Generators.filters_zi.append(sosfilt_zi(sos))

    scope = Oscilloscope(ylow=-1.1*Config.amp, yhigh=1.1*Config.amp)

    generation_thread = threading.Thread(target=generate_signal, args=())
    generation_thread.start()

    scope.init_plotting()


if __name__ == '__main__':
    main()