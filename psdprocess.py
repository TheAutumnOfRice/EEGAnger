from functools import partial
from typing import Optional, Callable, Any

import matplotlib.pyplot as plt
import mne
import numpy as np
from mne.time_frequency import psd_multitaper
from scipy import interpolate

from getdata import crop_by_clip
from preprocess import make_epoch_by_next_annotation

LEFT_CHANNELS = ['Fp1', 'F3', 'F7', 'FC3']
RIGHT_CHANNELS = ['Fp2', 'F4', 'F8', 'FC4']


def trans_to_db(a: np.ndarray):
    return 10 * np.log10(a * 1e12)


def trans_to_cubic_interpolate(x: np.ndarray, y: np.ndarray, smooth=0, step=1):
    tck = interpolate.splrep(x, y, s=smooth)
    xmin = x.min()
    xmax = x.max()
    xnew = np.arange(xmin, xmax, step)
    ynew = interpolate.splev(xnew, tck, der=0)
    return xnew, ynew


def DrawFiveLevel(raw, event_clips, id="S4"):
    S4 = crop_by_clip(raw, event_clips, id)
    S4E = make_epoch_by_next_annotation(S4)
    for i in ["1", "2", "3", "4", "5"]:
        S4E[i].plot_psd(average=True, fmax=50, show=False)
        plt.ylim([20, 50])
        plt.title(f"Level = {i}")
        plt.show()


def DrawClips(raw, event_clips, ids=[]):
    for i in ids:
        S = crop_by_clip(raw, event_clips, i)
        S.plot_psd(average=True, fmax=50, show=False, )
        plt.ylim([-5, 40])
        plt.title(f"ID: {i}")
        plt.show()


def draw_specgram(inst, vmin=100, vmax=160, cmap="viridis", ymin=0, ymax=50, ax=None):
    if ax is None:
        ax = plt
    _data = inst._data.copy()
    _data = _data.mean(axis=0)
    ax.specgram(_data * 1e6, Fs=inst.info["sfreq"], cmap=cmap, vmin=vmin, vmax=vmax)
    ax.ylim(ymin, ymax)


class PSDS:
    def __init__(self, inst: mne.epochs.Epochs = None, times: Optional[np.ndarray] = None,
                 psds: Optional[np.ndarray] = None, freqs: Optional[np.ndarray] = None, **kwargs):
        self.psds: np.ndarray
        self.times: np.ndarray
        self.freqs: np.ndarray
        self._inst = None
        self._L = 0 if "fmin" not in kwargs else kwargs["fmin"]
        self._R = np.inf if "fmax" not in kwargs else kwargs["fmax"]

        if inst is not None:
            self._inst = inst
            if psds is None and freqs is None and times is None:
                self.psds, self.freqs = psd_multitaper(inst, **kwargs)
                self.times = inst.events[:, 0] / 1000
        if psds is not None:
            self.psds = psds
        if freqs is not None:
            self.freqs = freqs
        if times is not None:
            self.times = times

    @property
    def shape(self):
        return self.psds.shape

    @property
    def ndim(self):
        return self.psds.ndim

    def __len__(self):
        return len(self.psds)

    @property
    def lfreq(self):
        return min(self.freqs)

    @property
    def rfreq(self):
        return max(self.freqs)

    def group_freq(self, lfreq=0, rfreq=np.inf):
        ind = (lfreq <= self.freqs) & (self.freqs < rfreq)
        f2 = self.freqs[ind]
        p2 = self.psds.swapaxes(0, -1)[ind].swapaxes(0, -1)
        return PSDS(freqs=f2, psds=p2, times=self.times, fmin=lfreq, fmax=rfreq, inst=self._inst)

    def select_channel(self, picks, caxis=1):
        assert self._inst is not None
        num = np.arange(len(self._inst.ch_names))
        ind = np.zeros_like(num)
        for i in picks:
            ind |= (num == i)
        p2 = self.psds.swapaxes(0, caxis)[ind].swapaxes(0, caxis)
        return PSDS(freqs=self.freqs, psds=p2, times=self.times, fmin=self._L, fmax=self._R, inst=self._inst)

    def average_channel(self, caxis=1, keepdims=False):
        p2 = self.psds.mean(axis=caxis, keepdims=keepdims)
        return PSDS(freqs=self.freqs, psds=p2, times=self.times, fmin=self._L, fmax=self._R, inst=self._inst)

    def average_freq(self, soft=1):
        tmp = self.map_freq(np.mean)
        pc = partial(np.convolve, v=np.ones((soft,)) / soft, mode='same')
        return np.apply_along_axis(pc, -1, tmp)

    def map_freq(self, fun: Callable[[np.ndarray], Any]):
        return np.apply_along_axis(fun, -1, self.psds)


def PlotPSD(inst, event_clip, lfreq, rfreq, mean_soft=1, cubic=True, smooth=0, step=1, vmin=20, vmax=40,
            show_anger=True, anger_cubic=True, anger_smooth=0, anger_step=1,
            show_events=[], events_color=[], events_dict={},
            ax=None):
    print("Ploting...")
    if ax is None:
        ax = plt.subplot(111)
    SP = PSDS(inst=inst)
    start_time = event_clip["start_time"]
    PG = SP.group_freq(lfreq, rfreq)
    LG = PG.select_channel([0, 2, 4, 8]).average_channel()
    RG = PG.select_channel([1, 3, 5, 7]).average_channel()
    LA = trans_to_db(LG.average_freq(mean_soft))
    RA = trans_to_db(RG.average_freq(mean_soft))
    TIM = SP.times - start_time
    if cubic:
        _, LA = trans_to_cubic_interpolate(TIM, LA, smooth, step)
        TIM, RA = trans_to_cubic_interpolate(TIM, RA, smooth, step)
    if show_anger:
        ax2 = ax.twinx()
        evts = event_clip["events"]
        ind = (evts[:, 2] >= 1) & (evts[:, 2] <= 5)
        evts = evts[ind]
        X = evts[:, 0] - start_time
        Y = evts[:, 2]
        if anger_cubic:
            X, Y = trans_to_cubic_interpolate(X, Y, anger_smooth, anger_step)
        ax2.fill_between(X, Y, color='gray', alpha=0.3, zorder=-99)
        ax2.set_ylim(0, 6)
        ax2.set_yticks([1, 2, 3, 4, 5])
        ax2.set_yticklabels(['L1', 'L2', 'L3', 'L4', 'L5'])
    ax.plot(TIM, LA, label="L")
    ax.plot(TIM, RA, label="R")
    evts = event_clip["events"]
    X = evts[:, 0] - start_time
    Y = evts[:, 2]
    for i, e in enumerate(show_events):
        ind = Y == e
        fg = True
        for j in X[ind]:
            ax.axvline(j, alpha=0.4, color=f"C{i + 2}" if events_color == [] else events_color[i],
                       label=None if not fg else str(e) if e not in events_dict else events_dict[e])
            fg = False

    ax.set_ylabel("μV²/Hz (dB)")
    ax.set_xlabel("Time (s)")
    ax.set_ylim(vmin, vmax)
    ax.legend()
