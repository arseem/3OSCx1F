import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Sine import SineOscillator
import threading




def data_update(i, ax, x, y, sin, fs, freq, size, amp, ln):
    y.append(next(sin))
    x.append(i*(1/fs))
    
    ax.set_xlim(x[-size], x[-1]) if len(y)>size else plt.xlim(0, size*1/fs)
    ax.set_ylim(-amp*1.1, amp*1.1)

    ln.set_data(x, y)
    return ln,


def main():
    fs = 100
    freq = 1
    amp = 1
    sin = iter(SineOscillator(freq, amp=amp, sample_rate=fs))
    size = 255
    x = []
    y = []


    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    ln, = ax.plot([], [])

    plt.title(f'Sine,\tf={freq},\tA={amp},\t$f_s$={fs}')
    plt.ylabel('sin(t)')
    plt.xlabel('t[s]')

    ani = FuncAnimation(fig, data_update, fargs=(ax, x, y, sin, fs, freq, size, amp, ln), interval=1000/fs, blit=True)
    plt.show()

if __name__ == '__main__':
    main()