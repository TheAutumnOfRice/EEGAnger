import matplotlib.pyplot as plt
from IPython import get_ipython
from mne.time_frequency import psd_multitaper, psd_array_multitaper

from getdata import *
from preprocess import *


def FixFun(EEG):
    OR = process_for_display(EEG)
    EPO = make_epoch(OR, timespan=4)
    super_fix(EPO, t=2.5)
    return EPO


def GetAngerList(event_clip, first_sample=True):
    if first_sample is True:
        offset = event_clip["start_time"]
    A = np.array(list(filter(lambda x: x[2] in [1, 2, 3, 4, 5], event_clip["events"])))
    X = A[:, 0]
    Y = A[:, 2]
    return X, Y


if __name__ == "__main__":
    # TODO 01 Multi-psd Diagram
    # TODO 02 Time-Freq Analysis
    get_ipython().run_line_magic("matplotlib", "qt")
    data_name = "02szc"
    raw = read_BDF_data(data_name)
    raw = eight_channel_mode(raw)
    events_timepoint, events_id = read_event_data(data_name, raw.info)
    events_timepoint, events_id = filter_events(events_timepoint, events_id, lambda x: x not in [401, 402])

    event_clips = preprocess_events(events_timepoint, events_id)
    # Anotation

    ano = mne.annotations_from_events(event_clips[3]["events"], 1, lambda x: str(int(x)))
    ano += mne.annotations_from_events(event_clips[5]["events"], 1, lambda x: str(int(x)))
    raw.set_annotations(ano)

    """S4 Test
    S4=crop_by_clip(raw,event_clips,"S4")
    S4E = make_epoch_by_next_annotation(S4)
    for i in ["1","2","3","4","5"]:
        S4E[i].plot_psd(average=True,fmax=50,show=False)
        plt.ylim([20,50])
        plt.title(f"Level = {i}")
        plt.show()
    # raw_plot(S4,decim=10)
    """
    OR1 = FixFun(crop_by_clip(raw, event_clips, "S1"))
    S2 = FixFun(crop_by_clip(raw, event_clips, "S2"))
    OR2 = FixFun(crop_by_clip(raw, event_clips, "S3"))
    S4 = FixFun(crop_by_clip(raw, event_clips, "S4"))
    OR3 = FixFun(crop_by_clip(raw, event_clips, "S5"))
    S6 = FixFun(crop_by_clip(raw, event_clips, "S6"))
    # Convert
    psds, freqs = psd_multitaper(S6)
