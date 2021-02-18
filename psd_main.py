from IPython import get_ipython

from getdata import *
from preprocess import *
from psdprocess import *


def FixFun(EEG):
    EPO = make_epoch(EEG, 0, 8)
    auto_fix(EPO, 2)
    return EPO


if __name__ == "__main__":
    # TODO 01 Multi-psd Diagram
    # TODO 02 Time-Freq Analysis
    get_ipython().run_line_magic("matplotlib", "qt")
    data_name = "03zzh"
    raw = read_BDF_data(data_name)
    raw = eight_channel_mode(raw)
    events_timepoint, events_id = read_event_data(data_name, raw.info)
    # events_timepoint, events_id = filter_events(events_timepoint,events_id,lambda x:x not in [401,402])

    event_clips = preprocess_events(events_timepoint, events_id)
    event_clips[0]["start_time"] += 100
    # Anotation

    ano = mne.annotations_from_events(event_clips[3]["events"], 1, lambda x: str(int(x)))
    ano += mne.annotations_from_events(event_clips[5]["events"], 1, lambda x: str(int(x)))
    raw.set_annotations(ano)

    # DrawFiveLevel(raw,event_clips,"S6")
    # DrawClips(raw,event_clips,["S1","S4"])
    # raw_plot(S4,decim=10)
    # OR1 = FixFun(crop_by_clip(raw, event_clips, "S1"))
    # R2 = crop_by_clip(raw,event_clips,"S2")
    # R2 = process_for_display(R2)
    # S2 = FixFun(crop_by_clip(raw, event_clips, "S2"))
    # OR2 = FixFun(crop_by_clip(raw, event_clips, "S3"))
    S4 = FixFun(crop_by_clip(raw, event_clips, "S4"))
    # R4 = crop_by_clip(raw,event_clips,"S4")
    # R4 = process_for_display(R4)
    # draw_specgram(raw)
    # see_clip()
    # OR3 = FixFun(crop_by_clip(raw, event_clips, "S5"))
    # S6 = FixFun(crop_by_clip(raw, event_clips, "S6"))

    # See S4

    # plt.specgram
    # PlotPSD(OR1,event_clips[0],20,30,show_anger=False)
    AC = PSDS(S4).group_freq(20, 30).average_channel()
    FC = AC.average_freq(soft=60)
    FC = trans_to_db(FC)
    plt.plot(AC.times, FC)

    # PlotPSD(S2,event_clips[1],20,30,mean_soft=3,smooth=1,cubic=True,show_anger=False,anger_cubic=False,show_events=[401,402],
    #         events_color=['darkorange','moccasin'],events_dict={401:"WIN",402:"DIE"})
    # plt.plot()
