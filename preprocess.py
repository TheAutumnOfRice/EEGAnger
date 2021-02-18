import mne
import numpy as np


def process_for_display(raw: mne.io.edf.edf.RawEDF):
    raw.resample(256)
    raw.notch_filter(50)
    raw.filter(0.5, None)
    return raw


def see_clip(raw, start, end, decim='auto', process=False):
    if process:
        raw = process_for_display(raw)
    raw.plot(start=start, duration=end - start, clipping=None, decim=decim)


def make_epoch(EEG, label=1, timespan=1.0):
    EPO = mne.make_fixed_length_epochs(EEG, timespan, verbose=0)
    EPO.load_data()
    EPO.event_id = {str(label): label}
    EPO.events[:, 2] = label
    return EPO


def make_epoch_by_next_annotation(EEG, timespan=1.0, filt=None):
    # Require {desc:events_id}={str(int(events_id)):int(events_id)}
    EPO = mne.make_fixed_length_epochs(EEG, timespan, verbose=0)
    EPO.load_data()
    desc = EEG.annotations.description
    onset = EEG.annotations.onset
    EPO.event_id = dict(map(lambda x: (str(int(x)), int(x)), desc))
    next_ind = 0
    for ind, (x, _, _) in enumerate(EPO.events):
        t = x / 1000
        while next_ind < len(onset) and onset[next_ind] < t:
            next_ind += 1
        if next_ind >= len(onset):
            next_ind = len(onset) - 1
        EPO.events[ind][2] = int(desc[next_ind])

    return EPO


def epoch_zscore(epodata: np.ndarray):
    a = epodata.mean(axis=2)
    m = a.mean(axis=0)
    s = a.std(axis=0)
    z = (a - m) / s
    return z


def calc_drop(z, t):
    p = 1
    mz = z.max(axis=1)
    mask = np.array(mz > t)
    mask2 = mask.copy()
    L = len(mask)
    for i in range(len(mask)):
        mask2[i] = mask[i]
        if mask[i]:
            for t in range(p):
                if i - t > 0:
                    mask2[i - t - 1] = True
                if i + t < L - 1:
                    mask2[i + t + 1] = True
    return mask2


def check_fix(EPO, show=True):
    L = len(EPO)
    z = np.abs(epoch_zscore(EPO._data))
    mz = z.max(axis=1)
    mz.sort()
    for i in [0, 0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        t = mz[-1 - int(L * i)]
        if show:
            print("t=%.3f" % t, "BAD EPOCHS %d%%" % (sum(calc_drop(z, t)) / L * 100))
    tt = mz[-1 - int(L * 0.20)]
    if tt < 3:
        tt = 3
    if show:
        print(">Recommand< t = ", tt, " BAD EPOCHS %d%%" % (sum(calc_drop(z, tt)) / L * 100))
    return tt


def auto_fix(EPO: mne.Epochs, t=None):
    if t is None:
        t = check_fix(EPO, False)
    z = epoch_zscore(EPO._data)
    EPO.drop(calc_drop(z, t), "AUTOFIX")


def super_fix(EPO: mne.Epochs, t=None, show=True):
    total = 0
    L = len(EPO)
    while True:
        if t is None:
            t = check_fix(EPO, False)
        z = epoch_zscore(EPO._data)
        mask = calc_drop(z, t)
        now = np.sum(mask)
        if now > 0:
            total = total + now
            EPO.drop(calc_drop(z, t), "SUPERFIX", verbose=0)
        else:
            break
    if show:
        print("SUPER FIX: ", total, '/', L)


def eight_channel_mode(raw: mne.io.edf.edf.RawEDF, mode=0):
    """
    只显示八个重点Channel来加速
    :param raw: 原数据
    :param mode: 0:前额模式
    :return: 剪切channels之后的
    """
    CutDict = {
        0: ['Fp1', 'Fp2', 'F3', 'F4', 'F7', 'F8', 'FC3', 'FC4']
    }
    if isinstance(mode, list):
        choose = mode
    else:
        choose = CutDict[mode]
    raw = raw.drop_channels(list(filter(lambda x: x not in choose, raw.ch_names)))
    return raw


def raw_plot(raw, **kwargs):
    kwargs.setdefault("decim", 10)
    kwargs.setdefault("clipping", None)
    kwargs.setdefault("highpass", 0.5)
    kwargs.setdefault("block", True)
    kwargs.setdefault("remove_dc", True)
    raw.plot(**kwargs)
