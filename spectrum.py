from soundfile import read as readSound
import numpy as np
from enum import Enum
from scipy.signal import get_window, stft, check_COLA, check_NOLA
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from typing import Callable
from io import BytesIO
from PIL.Image import Image, new as newImage, open as openImage
from pprint import pprint

class AudioSpectre:

    MIN_DECIBEL_LEVEL: int = -60
    DPI: int = 200
    DROP_LEVEL: float = 0.9 # drop spike if it is <DROP_LEVEL> percent lower

    class Scale(Enum):
        AUTO = 0
        LOGARITHMIC = 1
        LINEAR = 2

    class Limits(Enum):
        AUTO = 0
        FIT_TO_DATA = 1
        FULL = 2

    def __init__(self, file: str | BytesIO, window: str = 'blackman', window_size: int = 2000, overlap: int = 3 * 2000 // 4, fft_size: int = 10000):
        try:
            if (isinstance(file, str)):
                self.filename: str = file
            else:
                self.filename: str = 'audio'
            sound = readSound(file)
            self.bins: np.ndarray = sound[0]
            self.frequency: int = sound[1]
        except Exception as error:
            raise error
        
        self.windowSize: int = window_size
        self.fftSize: int = fft_size
        self.overlap: int = overlap
        self.window: str = window
        self.stft_f: np.ndarray | None = None
        self.stft_t: np.ndarray | None = None
        self.stft_Zxx: np.ndarray | None = None
        self.stft_plot: bytes | None = None
        self.plot: bytes | None = None
        self.scale: AudioSpectre.Scale = self.Scale.AUTO
        self.limits: AudioSpectre.Limits = self.Limits.AUTO

    @property
    def COLASatisfied(self) -> bool:
        return check_COLA(get_window(self.window, self.windowSize), self.windowSize, self.overlap)
    
    @property
    def NOLASatisfied(self) -> bool:
        return check_NOLA(get_window(self.window, self.windowSize), self.windowSize, self.overlap)
    
    def __buildSTFT(self) -> None:
        f, t, Zxx = stft(self.bins, fs=self.frequency, window=self.window, nperseg=self.windowSize, noverlap=self.overlap, nfft=self.fftSize)
        self.stft_f, self.stft_t, self.stft_Zxx = f, t, 20*np.log10(np.abs(Zxx[:-1, :-1]) / np.max(abs(Zxx[:-1, :-1])))
        for line, num in zip(*np.where(self.stft_Zxx < self.MIN_DECIBEL_LEVEL)):
            self.stft_Zxx[line, num] = self.MIN_DECIBEL_LEVEL
        
    @property
    def STFT(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.stft_f is None and self.stft_t is None and self.stft_Zxx is None:
            self.__buildSTFT()
        return (self.stft_f, self.stft_t, self.stft_Zxx)
    
    def __buildSTFTPlot(self) -> None:
        f, t, Zxx = self.STFT
        fig = plt.figure(figsize=[13.5, 7], dpi=self.DPI, frameon=False)

        scale = self.autoScale()
        f_min, f_max = self.autoLimits()
        if f_min == 0 and scale == self.Scale.LOGARITHMIC:
            f_min = 1
        
        f_labels = self.getFrequencyLabels((f_min, f_max), scale=scale)
        ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')


        if scale == self.Scale.LOGARITHMIC: ax.set_yscale('symlog')
        
        for freq in f_labels:
            lbl = ax.text(t[-1] * 1.003, freq, f'{self.getLabelText(freq)} -', 
                          size=18, color='white', horizontalalignment='right', 
                          verticalalignment='center').set_path_effects(
                              [pe.withStroke(linewidth=2, foreground='k')])
        

        ax.set_ylim((f_min, f_max))

        ax.pcolormesh(t, f, Zxx, cmap=plt.get_cmap('inferno'), shading='auto')
        with BytesIO() as io:
            fig.savefig(io, format='png', facecolor='black', transparent=False)
            io.seek(0)
            self.stft_plot = io.read()

    @property
    def STFTPlot(self) -> bytes:
        if self.stft_plot is None:
            self.__buildSTFTPlot()
        return self.stft_plot
    
    def __buildPlot(self) -> None:
        fig = plt.figure(figsize=[13.5, 1.5], dpi=self.DPI, frameon=True)
        ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.plot(self.bins)
        ax.set_xlim(0, len(self.bins))
        height = max(self.bins) - min(self.bins)
        ax.set_ylim(min(self.bins) - 0.03 * height, max(self.bins) + 0.03 * height)
        filename = ax.text(0, 0, f'    {self.filename} ({len(self.bins) / self.frequency:.1f} sec)', size=18, color='white', horizontalalignment='left', verticalalignment='center')
        filename.set_path_effects([pe.withStroke(linewidth=2, foreground='k')])
        ax.grid()
        with BytesIO() as io:
            fig.savefig(io, format='png', facecolor='black', transparent=False)
            io.seek(0)
            self.plot = io.read()


    @property
    def Plot(self) -> bytes:
        if self.plot is None:
            self.__buildPlot()
        return self.plot
    
    @property
    def Spectre(self) -> bytes:
        img1 = BytesIO()
        img1.write(self.STFTPlot)
        img1.seek(0)
        stft_image = openImage(img1, mode='r')
        img2 = BytesIO()
        img2.write(self.Plot)
        img2.seek(0)
        audio_image = openImage(img2, mode='r')
        result = newImage(stft_image.mode, (stft_image.width, stft_image.height + audio_image.height))
        result.paste(stft_image, (0, 0))
        result.paste(audio_image, (0, stft_image.height))
        with BytesIO() as io:
            result.save(io, format='png')
            io.seek(0)
            return io.read()
        
    @property
    def globalSpikes(self) -> dict[float, float]:
        class Sign(Enum):
            UNDEFINED = 0
            POS = 1
            NEG = 2

        f, _, Zxx = self.STFT

        max_spike, min_spike = None, None

        spikes: dict[float, float] = {}

        prev_sign = Sign.UNDEFINED

        for i in range(0, len(Zxx) - 1):
            cur_level = np.average(Zxx[i + 1])
            dval_i = cur_level - np.average(Zxx[i])

            sign = prev_sign
            if dval_i < 0: sign = Sign.NEG
            elif dval_i > 0: sign = Sign.POS

            if prev_sign == Sign.POS and sign == Sign.NEG:
                spikes[float(f[i])] = float(cur_level)
                if max_spike is None or float(cur_level) > max_spike: max_spike = float(cur_level)
                if min_spike is None or float(cur_level) < min_spike: min_spike = float(cur_level)

            prev_sign = sign

        delta = max_spike - min_spike
        for spike in list(spikes.keys()):
            if spikes[spike] < max_spike - 0.9 * delta:
                spikes.pop(spike)

        return spikes
    
    def autoLimits(self, fit_to_data: bool = True) -> tuple[float, float]:
        if self.limits == self.Limits.AUTO:
            spikes = self.globalSpikes
            min = np.min(list(spikes.keys()))
            max = np.max(list(spikes.keys()))
            delta = max - min
            min = min - 0.1 * delta
            max = max + 0.1 * delta
            if min < 0: min = 0
            if max > self.frequency // 2: max = self.frequency // 2
            return min, max
        elif self.limits == self.Limits.FIT_TO_DATA:        
            spikes = self.globalSpikes
            min = np.min(list(spikes.keys()))
            max = np.max(list(spikes.keys()))
            delta = max - min
            min = min - 0.1 * delta
            max = max + 0.1 * delta
            if min < 0: min = 0
            if max > self.frequency // 2: max = self.frequency // 2
            return min, max
        elif self.limits == self.Limits.FULL:
            return 0, self.frequency // 2
    
    def autoScale(self) -> Scale:
        if self.scale == self.Scale.AUTO:
            return self.Scale.LINEAR
        return self.scale
    
    @classmethod
    def getLabelText(cls, frequency: float) -> str:
        suffix_pow = 0
        while frequency > 1000.0:
            suffix_pow += 1
            frequency = frequency / 1000.0
        
        suffix = ['', 'k', 'M', 'G'][suffix_pow]
        freq_str = f'{frequency:.2f}'.strip('0').strip('.')
        return f'{freq_str} {suffix}Hz'
    
    @classmethod
    def getFrequencyLabels(cls, f_lims: list[float], scale: Scale = Scale.LINEAR, labels_count: int = 5) -> list[float]:
        
        if scale == cls.Scale.LOGARITHMIC:
            step = (f_lims[1] / f_lims[0]) ** (1 / (labels_count + 1))
            labels = [f_lims[0] * step ** n for n in range(1, labels_count + 1)]
        else: 
            step = (f_lims[1] - f_lims[0]) / (labels_count + 1)
            labels = [f_lims[0] + step * n for n in range(1, labels_count + 1)]
        
        return labels


if __name__ == '__main__':
    audio = AudioSpectre('test.ogg', window='hann')
    print(audio.COLASatisfied, audio.NOLASatisfied)

    with open('test_both.png', 'wb') as file:
        file.write(audio.Spectre)

    test = []
    for line in audio.STFT[2]:
        test.append(np.average(line))
    plt.figure(figsize=[10, 4])
    plt.plot(test)
    plt.grid()
    plt.savefig('test_graph.png')

    #pprint(audio.globalSpikes())
    #fig.savefig('test.png', transparent=False)

    
    