from pyecharts import options as opts
from pyecharts.charts import Line


def GetGrad(allPeopleList: {}):
    Grad_l = (
        Line()
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="Grad"),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True, link=[{"xAxisIndex": "all"}]
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=False
            ),
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_top="top",
                pos_left="right",
                orient="vertical"
            )
        )
    )
    for user in allPeopleList:
        for description in allPeopleList[user]:
            if allPeopleList[user][description]['active'] == 1:
                anger = allPeopleList[user][description]['data']
                Grad_l.add_xaxis(xaxis_data=anger.output['AC'].times[1:anger.output['FC'].size])
                Grad_l.add_yaxis(y_axis=anger.output['Grad_FC'], series_name=description, is_symbol_show=False)
            else:
                continue
    Grad_l = Grad_l.dump_options_with_quotes()
    return Grad_l


def GetKde(allPeopleList: {}):
    kde_l = (
        Line()
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="Kde"),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True, link=[{"xAxisIndex": "all"}]
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=False
            ),
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_top="top",
                pos_left="right",
                orient="vertical"
            )
        )
    )
    for user in allPeopleList:
        for description in allPeopleList[user]:
            if allPeopleList[user][description]['active'] == 1:
                anger = allPeopleList[user][description]['data']
                kde_l.add_xaxis(xaxis_data=anger.output['X'])
                kde_l.add_yaxis(y_axis=anger.output['dens'], series_name=description, is_symbol_show=False)
            else:
                continue
    kde_l = kde_l.dump_options_with_quotes()
    return kde_l


def GetStateAnger(allPeopleList: {}):
    stateanger_l = (
        Line()
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="State Anger"),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True, link=[{"xAxisIndex": "all"}]
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=False
            ),
            legend_opts=opts.LegendOpts(
                type_="scroll",
                pos_top="top",
                pos_left="right",
                orient="vertical"
            )
        )
    )
    for user in allPeopleList:
        for description in allPeopleList[user]:
            if allPeopleList[user][description]['active'] == 1:
                anger = allPeopleList[user][description]['data']
                stateanger_l.add_xaxis(xaxis_data=anger.output['AC'].times)
                stateanger_l.add_yaxis(y_axis=anger.output['FC'], series_name=description, is_symbol_show=False)
            else:
                continue
    stateanger_l = stateanger_l.dump_options_with_quotes()
    return stateanger_l
