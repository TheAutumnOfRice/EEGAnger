from pathlib import *
from typing import Union, Tuple, List

import scipy.stats as st

from getdata import *
from preprocess import *
from psdprocess import *


class FixFun:
    def __init__(self, use_fix=True, auto_level=2):
        self.use_fix = use_fix
        self.auto_level = auto_level

    def __call__(self, EEG):
        EPO = make_epoch(EEG, 0, 8)
        if self.use_fix:
            auto_fix(EPO, self.auto_level)
        return EPO


###dfs
class anger:
    def __init__(self, _a: List["anger"] = None):
        self.soft = -1
        self.low = -1
        self.high = -1
        self.time_overlap = -1
        self.mode = ""
        self.output = {}
        self.peoplename = ""
        self._a = _a

    def getpeoplelist(self, loaction: str):
        p = Path(loaction)
        for i in p.iterdir():
            if (i.exists('event.txt') and i.exists('data.bdf')) is true:
               
    def _merge(self, check_list):
        if self._a is None:
            return None
        """
        Check list:
        [
            "peoplename",
            "mode",
            "time_overlap"
        ]
        """

        for a in self._a:
            flag = False
            for k in check_list:
                if getattr(a, k) != getattr(self, k):
                    flag = True
                    break
            if not flag:
                return a
        return None

    def loaddata(self, peoplename, time_overlap: Union[int, Tuple[int, int]] = 150, mode='S4', use_fix=False,
                 auto_level=2):
        self.peoplename = peoplename
        # Merge Peoplename -> event_clips, raw
        CL = ["peoplename",
              "mode",
              "time_overlap"]
        # CL.append("peoplename")
        D = self._merge(CL)
        if D is not None:
            event_clips = self.output['event_clips'] = D.output["event_clips"]
            raw = self.output["raw"] = D.output["raw"]
        else:
            raw = read_BDF_data(peoplename)
            raw = eight_channel_mode(raw)
            events_timepoint, events_id = read_event_data(peoplename, raw.info)
            event_clips = preprocess_events(events_timepoint, events_id)
            self.output['event_clips'] = event_clips
            self.output['raw'] = raw

        self.time_overlap = time_overlap
        self.mode = mode
        valid = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        assert mode in valid, "Mode只能为" + ",".join(valid) + "中的一个！"
        mode_value = int(mode[1]) - 1
        if isinstance(time_overlap, int):
            if mode_value <= 4:
                event_clips[mode_value]['end_time'] += self.time_overlap
            if mode_value >= 1:
                event_clips[mode_value]['start_time'] -= self.time_overlap
        else:
            start_offset, end_offset = self.time_overlap
            event_clips[mode_value]['start_time'] -= start_offset
            event_clips[mode_value]['end_time'] += end_offset

        # Merge FixFun
        CL = []
        CL = [
            "use_fix",
            "auto_level"
        ]
        D = self._merge(CL)
        if D is not None:
            S = self.output.['S'] = D.output.['S']
        else:
            S = FixFun(use_fix=use_fix, auto_level=auto_level)(crop_by_clip(raw, event_clips, self.mode))
            self.output['S'] = S
        return self

    def get_description(self, peoplename: str, value_list: dict):
        str1 = str(value_list)  # 那个啥，这个重点在前面
        str2 = peoplename
        str = str1 + str2
        return str

    def compute(self, soft=10, low=20, high=30):
        self.soft = soft
        self.low = low
        self.high = high
        # Merge S
        S = self.output['S']

        AC = PSDS(S).group_freq(self.low, self.high).average_channel()
        # Merge Low High
        AC.times = AC.times - AC.times[1]
        FC = AC.average_freq(soft=self.soft)
        FC = trans_to_db(FC)
        self.output['AC'] = AC
        self.output['FC'] = FC
        self.output.setdefault('up', {})
        self.output.setdefault('down', {})
        Diff_FC = np.diff(FC)
        PerTimes = np.diff(AC.times)
        Grad_FC = Diff_FC / PerTimes

        X = Grad_FC.copy()
        scipy_kde = st.gaussian_kde(X)  # 高斯核密度估计
        X.sort()
        dens = scipy_kde.evaluate(X)
        self.output['dens'] = dens
        self.output['X'] = X
        self.output["Grad_FC"] = Grad_FC
        self.output["PerTimes"] = PerTimes
        return self

    def get_truncedExp(self, threshold=0.):
        dens = self.output['dens']
        X = self.output['X']
        e1 = X[X > threshold] * dens[X > threshold]
        e2 = X[X < -threshold] * dens[X < -threshold]
        return np.sum(e1), np.sum(e2)

    def get_middle(self, threshold=0.):
        c1 = self.output['Grad_FC'][self.output['Grad_FC'] >= threshold]
        c2 = self.output['Grad_FC'][self.output['Grad_FC'] <= threshold]
        return np.median(c1), np.median(c2)

    def get_average(self, threshold=0.):
        c1 = self.output['Grad_FC'][self.output['Grad_FC'] >= threshold]
        c2 = self.output['Grad_FC'][self.output['Grad_FC'] <= threshold]
        return np.average(c1), np.average(c2)

    def drawGrad(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(self.output['AC'].times[1:self.output['FC'].size], self.output['Grad_FC'], label=self.peoplename)
        plt.legend()

    def drawkde(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(self.output['X'], self.output['dens'], label=self.peoplename)
        plt.tick_params(labelsize=20)
        font = {'size': 20}
        plt.xlabel('变量', font)
        plt.ylabel('概率密度函数', font)
        plt.legend(fontsize=15)

    def drawstateanger(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(self.output['AC'].times, self.output['FC'], label=self.peoplename)
        plt.legend()


a = anger()
people_list = ['01zlh', '02szc', '03zzh', '04zzm']
data = {}
for people in people_list:
    data[people] = anger().loaddata(peoplename=people, time_overlap=(300, 300)).compute()

# Draw StateAnger
lup = {}
ldown = {}
for th in np.linspace(0, 0.1, 500):
    for k, v in data.items():
        lup.setdefault(k, [])
        ldown.setdefault(k, [])

        # v.drawstateanger()
        # v.drawkde()
        up, down = v.get_truncedExp(th)
        lup[k] += [up]
        ldown[k] += [down]
        up = round(up, 3)
        down = -round(down, 3)
        print(k, ":", "UP:", up, 'DOWN:', down)

plt.figure()
for k, v in lup.items():
    plt.plot(v, label=k)
plt.title("UP")
plt.legend()
plt.show()

plt.figure()
for k, v in ldown.items():
    plt.plot(v, label=k)
plt.title("DOWN")
plt.legend()
plt.show()

plt.plot()

plt.axvline(x=300)
plt.axvline(x=1632 - 150)

plt.show()
