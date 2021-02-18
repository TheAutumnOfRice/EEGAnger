import datetime
import json
import os

import mne
import numpy as np

from config import data_dir


def read_BDF_data(data_name: str):
    # Read BDF
    raw: mne.io.edf.edf.RawEDF = mne.io.read_raw_bdf(os.path.join(data_dir, data_name, "data.bdf"), preload=True)
    # Remove Unused Channels
    try:
        raw.drop_channels(["ECG", "HEOR", "HEOL", "VEOU", "VEOL"])
    except:
        pass
    # Montage
    standard_montage = mne.channels.make_standard_montage("standard_1020")
    raw.set_montage(standard_montage)
    return raw


def read_event_data(data_name: str, bdf_info):
    # Read Exam Time
    # with open(os.path.join(data_dir, data_name, "recordInformation.json"), "r") as f:
    #         record_info = json.load(f)
    # exam_time_str = record_info["ExamTime"]
    exam_time_datetime = bdf_info["meas_date"].replace(tzinfo=None)
    exam_time_stamp = exam_time_datetime.timestamp()
    # Read Event TXT
    original_events_data = np.genfromtxt(os.path.join(data_dir, data_name, "event.txt"))
    events_timepoint = original_events_data[:, 0] / 1000 - exam_time_stamp
    events_id = original_events_data[:, 1].astype(np.int)
    return events_timepoint, events_id


def filter_events(events_timepoint, events_id, filt):
    return map(list, zip(*filter(lambda x: filt(x[1]), zip(events_timepoint, events_id))))


def preprocess_events(events_timepoint, events_id):
    # 获取分段时间点
    etm = np.array(events_timepoint)
    eid = np.array(events_id)
    event_clips = []
    clip_start = [11, 21, 31, 41, 51, 61]
    clip_end = [12, 22, 32, 42, 52, 62]
    clip_name = ["S1", "S2", "S3", "S4", "S5", "S6"]
    for cs, ce, cn in zip(clip_start, clip_end, clip_name):
        start_id = np.argmax(eid == cs)
        end_id = np.argmax(eid == ce)
        # 实验后的评级前移：S4后和S6后
        if cn in ["S4", "S6"]:
            end_id += 1
            eid[end_id - 1], eid[end_id] = eid[end_id], eid[end_id - 1]
        start_time = etm[start_id]
        end_time = etm[end_id]
        total_time = end_time - start_time
        events_0 = etm[start_id + 1:end_id]
        events_1 = np.zeros_like(events_0)
        events_2 = eid[start_id + 1:end_id]

        events = np.c_[events_0, events_1, events_2]
        clip = dict(
            name=cn,
            start_id=start_id,
            end_id=end_id,
            start_time=start_time,
            end_time=end_time,
            total_time=total_time,
            events=events
        )
        event_clips.append(clip)
    return event_clips


def crop_by_clip(raw: mne.io.edf.edf.RawEDF, event_clips, name):
    print("Croping ... ", name)
    for clip in event_clips:
        if clip["name"] == name:
            new_raw = raw.copy()
            new_raw.crop(clip["start_time"], clip["end_time"])

            return new_raw
    raise ValueError("Name Not Found!")
