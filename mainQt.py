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
from PyQt6 import QtCore, QtGui, QtWidgets
import sys
from SigGen import Ui_MainWindow


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
    update = 1


@dataclass
class Config:
    freq = 5
    amp = 1

    filter_type = 0
    cutoff = 10
    order = 24

    length = int(1/freq*Global_data.fs*3)
    timebase = 0.001
    
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


class Oscilloscope():

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
        self.fig.canvas.manager.set_window_title('Oscilloscope')

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


    def _tick(self, i):
        # while len(Data.Y)<self.size:
        #     sleep(0.01)

        with Data.LOCK:
            #print('Reading Data')
            self.x = Data.X
            self.y = Data.Y
            self.y_pre = Data.Ytf

        self.ax.set_xlim(self.x[-self.size], self.x[-1]) if len(self.y)>self.size else self.ax.set_xlim(0, self.size*1/self.fs)
        self.ax.set_ylim(self.ylow, self.yhigh)

        self.ln.set_data(self.x[-self.size:], self.y[-self.size:])
        self.ln_pre.set_data(self.x[-self.size:], self.y_pre[-self.size:])
        
        if i%self.timebase*1000==0:
            self.ax.figure.canvas.draw()
            self.axf.figure.canvas.draw()

        if len(self.y)<self.size:
            self.axf.set_ylim(-100, 0)
            self.axf.set_xlim(0, self.fs/2)
            return self.ln, 

        else:
            xf = rfftfreq(self.size, 1/self.fs)
            yf = rfft(self.y[-self.size:])
            yf = np.where(abs(yf) > 0.0000000001, yf, 0.0000000001)
            yf_scale = 20*np.log10(np.abs(yf))
            self.lnf.set_data(xf, -max(yf_scale)+yf_scale)
            fill = self.axf.fill_between(xf, -max(yf_scale)+yf_scale, min(-max(yf_scale)+yf_scale), color=Appearance.color_front)

            if len(Generators.filters)>0:
                w = Generators.filters_freqz[0][0]
                h = Generators.filters_freqz[0][1]
                self.lnf_filt.set_data(w/2/3.14*self.fs, 20*np.log10(abs(h)))
                self.axf.set_ylim(min(-max(yf_scale)+yf_scale), max(20 * np.log10(abs(h))[:len(w)])) if min(-max(yf_scale)+yf_scale)>=-100 else self.axf.set_ylim(-100, max(20 * np.log10(abs(h))[:len(w)]))
            else:
                self.lnf_filt.set_data(xf, len(xf)*[self.yhigh])
                self.axf.set_ylim(min(-max(yf_scale)+yf_scale), 0)

            self.axf.set_xlim(0, self.fs/2)
        
        return self.ln, self.lnf, fill, self.ln_pre, self.lnf_filt, 


    def init_plotting(self):
        self.ani = FuncAnimation(self.fig, self._tick, interval=self.timebase*1000, blit=True)
        self.fig.show()

    def change_timebase(self):
        self.ani.event_source.interval = self.timebase*1000


def generate_signal():
    sleep(1)
    while True:
        start = perf_counter()

        with Data.LOCK:
            Data.I+=1
            Data.Ytf.append(next(Generators.signals[0]))
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
    if len(Generators.filters) > 0:
        if len(Data.Ytf) <= delay:
            Data.Y = (list(sosfilt(Generators.filters[0], Data.Ytf, zi=Generators.filters_zi[0]*Data.Ytf[0]))[0])
        else:
            Data.Y[-delay:] = (list(sosfilt(Generators.filters[0], Data.Ytf[-delay:], zi=Generators.filters_zi[0]*Data.Ytf[-delay]))[0])
    
    else:
        if len(Data.Ytf) <= delay:
            Data.Y = Data.Ytf     
        else:
            Data.Y[-delay:] = Data.Ytf[-delay:]        


def freq_dial_handler(value):
    Generators.signals[0].freq = Config.freq = value/10
    print(f'Frequency value changed {Generators.signals[0].freq}')

def amp_dial_handler(value, scope):
    Generators.signals[0].amp = Config.amp = value/10
    scope.ylow = -1.1*value/10
    scope.yhigh = 1.1*value/10
    print(f'Amplitude value changed {Generators.signals[0].amp}')

def timebase_dial_handler(value, scope):
    scope.timebase = value/100
    scope.change_timebase()
    print(f'Timebase value changed {scope.timebase}')

def length_dial_handler(value, scope):
    scope.size = int(value/10)
    print(f'Window length changed {scope.size}')

def filter_dial_handler(cutoff, order, ftype):
    with Data.LOCK:
        Generators.filters = []
        Generators.filters_freqz = []
        Generators.filters_zi = []
    if not ftype=='none':
        sos = butter(order, cutoff/10*2/Global_data.fs, output = 'sos', btype=ftype)
        w, h = sosfreqz(sos)
        with Data.LOCK:
            Generators.filters.append(sos)
            Generators.filters_freqz.append((w, h))
            Generators.filters_zi.append(sosfilt_zi(sos))

        print(f'New {ftype} filter |cutoff: {cutoff/10} |order: {order}')

    else:
        print('Filter removed')


def signal_change_handler(sig):
    with Data.LOCK:
        if sig=='sine':
            Generators.signals.append(SineOscillator(Config.freq, amp=Config.amp, sample_rate=Global_data.fs))
        elif sig=='sawtooth':
            Generators.signals.append(SawOscillator(Config.freq, amp=Config.amp, sample_rate=Global_data.fs))
        elif sig=='triangle':
            Generators.signals.append(TriangleOscillator(Config.freq, amp=Config.amp, sample_rate=Global_data.fs))
        elif sig=='square':
            Generators.signals.append(SquareOscillator(Config.freq, amp=Config.amp, sample_rate=Global_data.fs))
        Generators.signals = Generators.signals[-1:]
        


def main():
    Generators.signals.append(SawOscillator(Config.freq, amp=Config.amp, sample_rate=Global_data.fs))

    order = 24
    cutoff = 7
    sos = butter(order, cutoff*2/Global_data.fs, output = 'sos', btype='lowpass')
    w, h = sosfreqz(sos)
    Generators.filters.append(sos)
    Generators.filters_freqz.append((w, h))
    Generators.filters_zi.append(sosfilt_zi(sos))

    generation_thread = threading.Thread(target=generate_signal, args=(), daemon=True)
    generation_thread.start()

    scope = Oscilloscope(ylow=-1.1*Config.amp, yhigh=1.1*Config.amp)
    scope.init_plotting()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, scope, [freq_dial_handler, amp_dial_handler, length_dial_handler, timebase_dial_handler, filter_dial_handler, signal_change_handler])
    MainWindow.setWindowTitle("Signal Generator")
    MainWindow.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()