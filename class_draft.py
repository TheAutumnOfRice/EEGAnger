import scipy.stats as st
from IPython import get_ipython

from getdata import *
from preprocess import *
from psdprocess import *


# FC and AC 就不解释了，InterpolationMultiply是插值扩增的倍数，flag决定计算上升或下降，threshold是阈值；
def GetGradAverageAndmedian(FC, AC, InterpolationMultiply=10, flag='up', threshold=0):
    Diff_FC = np.diff(FC)

    PerTimes = np.diff(AC.times)
    Grad_FC = Diff_FC / PerTimes
    plt.plot(AC.times[1:FC.size], Grad_FC)
    interpTime = np.interp(np.linspace(1, FC.size, FC.size * InterpolationMultiply), np.linspace(1, FC.size, FC.size),
                           AC.times)

    interpGrad_FC = np.interp(interpTime, AC.times[0:FC.size - 1], Grad_FC)
    X = interpGrad_FC
    scipy_kde = st.gaussian_kde(X)  # 高斯核密度估计
    X.sort()

    dens = scipy_kde.evaluate(X)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(X, dens, c='green', label='核密度值')
    plt.tick_params(labelsize=20)
    font = {'size': 20}
    plt.xlabel('变量', font)
    plt.ylabel('概率密度函数', font)
    plt.legend(fontsize=15)
    plt.show()
    if (flag == 'up'):
        c1 = interpGrad_FC[interpGrad_FC >= threshold]

    else:
        c1 = interpGrad_FC[interpGrad_FC <= threshold]
    return np.average(c1), np.median(c1)


def FixFun(EEG):
    EPO = make_epoch(EEG, 0, 8)
    auto_fix(EPO, 2)
    return EPO


if __name__ == "__main__":
    data_name = ["01zlh", "02szc", "03zzh", "04zzm"]
    get_ipython().run_line_magic("matplotlib", "qt")
    plt.figure(1)
    for i in range(0, 4):
        raw = read_BDF_data(data_name[i])
        raw = eight_channel_mode(raw)
        events_timepoint, events_id = read_event_data(data_name[i], raw.info)
        event_clips = preprocess_events(events_timepoint, events_id)
        event_clips[3]["start_time"] -= 150
        event_clips[1]["end_time"] += 150
        # ano=mne.annotations_from_events(event_clips[3["events"],1,lambda x:str(int(x)))
        # ano+=mne.annotations_from_events(event_clips[5]["events"],1,lambda x:str(int(x)))
        # raw.set_annotations(ano)
        S = FixFun(crop_by_clip(raw, event_clips, "S6"))
        AC = PSDS(S).group_freq(20, 30).average_channel()
        FC = AC.average_freq(soft=60)
        FC = trans_to_db(FC)
        plt.plot(AC.times, FC)
        Diff_FC = np.diff(FC)
        InterpolationMultiply = 10
        PerTimes = np.diff(AC.times)
        Grad_FC = Diff_FC / PerTimes

        # interpTime = np.interp(np.linspace(1, FC.size, FC.size * InterpolationMultiply),
        #                        np.linspace(1, FC.size, FC.size), AC.times)
        #
        # interpGrad_FC = np.interp(interpTime, AC.times[0:FC.size - 1], Grad_FC)
        # Grad_FC=trans_to_db(Grad_FC)
        X = Grad_FC
        X = np.convolve(X, [1 / 10] * 10)
        X.sort()
        scipy_kde = st.gaussian_kde(X)  # 高斯核密度估计
        # sb.distplot(X)
        dens = scipy_kde.evaluate(X)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(X, dens, label=data_name[i])
        plt.tick_params(labelsize=20)
        font = {'size': 20}
        plt.xlabel('变量', font)
        plt.ylabel('概率密度函数', font)
        plt.legend(fontsize=15)


class a:
    """
    First:
    Second: ...
    """

    def __init__(self, soft=10, low=20, high=30, time_overlap=150, threshold=0, mode='S4'):
        self.soft = soft
        self.low = low
        self.high = high
        self.time_overlap = time_overlap
        self.mode = mode
        self.data = {}
        self.peoplename = None

    def loaddata(self, peoplename):
        self.peoplename = peoplename
        raw = read_BDF_data(peoplename)
        raw = eight_channel_mode(raw)
        events_timepoint, events_id = read_event_data(self.[i], raw.info)
        event_clips = preprocess_events(events_timepoint, events_id)

    def compute(self, soft=10, fixfun=False):
        if fixfun is None:
            fixfun = FixFun
        event_clips[3]["start_time"] -= self.time_overlap
        event_clips[3]["end_time"] += self.time_overlap
        if fixfun is not False:
            S = fixfun(crop_by_clip(raw, event_clips, self.mode))
        else:
            S = crop_by_clip(raw, event_clips, self.mode)
        AC = PSDS(S).group_freq(self.low, self.high).average_channel()
        FC = AC.average_freq(soft=self.soft)
        FC = trans_to_db(FC)
        self.output['AC'] = AC
        self.output['FC'] = FC
        self.output.setdefault('up', {})
        self.output.setdefault('down', {})
        Diff_FC = np.diff(FC)

        PerTimes = np.diff(AC.times)
        Grad_FC = Diff_FC / PerTimes
        # plt.plot(AC.times[1:FC.size], Grad_FC)
        # interpTime = np.interp(np.linspace(1, FC.size, FC.size * InterpolationMultiply),
        #                        np.linspace(1, FC.size, FC.size), AC.times)

        # interpGrad_FC = np.interp(interpTime, AC.times[0:FC.size - 1], Grad_FC)
        # X = interpGrad_FC
        scipy_kde = st.gaussian_kde(X)  # 高斯核密度估计
        X.sort()
        dens = scipy_kde.evaluate(X)
        self.output['dens'] = dens

    def get_truncedExp(self, threshold):
        dens = self.output['dens']
        interFC = self.output['interFC']
        return exp

    def get_middle(self, threshold):
        return mid

    def get_average(self, threshold):
        pass

        # self.output['up']['...'] = interpGrad_FC[interpGrad_FC >= self.threshold]
        #
        # c1 = interpGrad_FC[interpGrad_FC <= self.threshold]
        #
        # return X,scipy,dens,np.average(c1), np.median(c1),interpTime,interpGrad_FC

    def drawGrad(self, interpTime, interpGrad_FC, People=1):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(interpTime, interpGrad_FC, label=self.people[People])

    def drawkde(self, X, dens, People=1):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(X, dens, label=self.people[People])
        plt.tick_params(labelsize=20)
        font = {'size': 20}
        plt.xlabel('变量', font)
        plt.ylabel('概率密度函数', font)
        plt.legend(fontsize=15)
