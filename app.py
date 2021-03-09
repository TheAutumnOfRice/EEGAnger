import json

from flask import Flask, render_template, request

from anger import Anger
from getcharts import *
from config import data_dir

app = Flask(__name__, static_folder="templates")

# name 下面加入description 不写入就默认 写入就修改

allPeopleList = {}


# user(zy) ->{
#   description(“zy soft:10 low:......”) -> {
#        'data': Anger Object
#        'active': 0 or 1
#   },
# }

@app.route("/")
def bootstrap():
    return render_template("bootstrap.html", peopleList=Anger.getpeoplelist(data_dir), allPeopleList=allPeopleList)


@app.route("/getChart")
def get_chart():
    Grad_l = GetGrad(allPeopleList)
    kde_l = GetKde(allPeopleList)
    stateanger_l = GetStateAnger(allPeopleList)

    list = json.dumps([Grad_l, kde_l, stateanger_l])
    return list


@app.route("/changeActive", methods=['POST'])
def change_active():
    data = request.get_data(as_text=True)
    data = json.loads(data)
    allPeopleList[data['peoplename']][data['description']]['active'] = not \
        allPeopleList[data['peoplename']][data['description']]['active']
    return get_chart()


@app.route("/deleteMember", methods=['POST'])
def delete_member():
    data = request.get_data(as_text=True)
    data = json.loads(data)
    del allPeopleList[data['peoplename']][data['description']]
    return get_chart()


@app.route("/searchMember", methods=['POST'])
def search_member():
    data = request.get_data(as_text=True)
    data = json.loads(data)
    paramList = allPeopleList[data['peoplename']][data['description']]['data'].param
    return json.dumps(paramList)


@app.route("/setMember", methods=['POST'])
def set_member():
    try:
        peoplename = request.form['peoplename']
        soft = int(request.form['soft'])
        low = int(request.form['low'])
        high = int(request.form['high'])
        time_overlap1 = int(request.form['time_overlap1'])
        mode = request.form['mode']
        auto_level = int(request.form['auto_level'])
        if 'use_fix' in request.form:
            use_fix = True
        else:
            use_fix = False

        if 'time_overlap2' in request.form:
            a = Anger().make({
                'peoplename': peoplename,
                'time_overlap': (time_overlap1, int(request.form['time_overlap2'])),
                'mode': mode,
                'use_fix': use_fix,
                'auto_level': auto_level,
                'soft': soft,
                'low': low,
                'high': high
            })
        else:
            a = Anger().make({
                'peoplename': peoplename,
                'time_overlap': time_overlap1,
                'mode': mode,
                'use_fix': use_fix,
                'auto_level': auto_level,
                'soft': soft,
                'low': low,
                'high': high
            })
        description = a.get_description()
    except Exception as e:
        return json.dumps(str(e))
    else:
        if peoplename not in allPeopleList:
            allPeopleList[peoplename] = {}
        allPeopleList[peoplename][description] = {'data': a, 'active': True}
        return json.dumps("SUCCESS")


@app.route("/editMember", methods=['POST'])
def edit_member():
    try:
        # get origin object
        data = allPeopleList[request.form['prepeoplename']][request.form['description']]['data']
        activeState = allPeopleList[request.form['prepeoplename']][request.form['description']]['active']
        # process form
        peoplename = request.form['peoplename']
        soft = int(request.form['soft'])
        low = int(request.form['low'])
        high = int(request.form['high'])
        time_overlap1 = int(request.form['time_overlap1'])
        mode = request.form['mode']
        auto_level = int(request.form['auto_level'])
        if 'use_fix' in request.form:
            use_fix = True
        else:
            use_fix = False

        if 'time_overlap2' in request.form:
            data = data.make({
                'peoplename': peoplename,
                'time_overlap': (time_overlap1, int(request.form['time_overlap2'])),
                'mode': mode,
                'use_fix': use_fix,
                'auto_level': auto_level,
                'soft': soft,
                'low': low,
                'high': high
            })
        else:
            data = data.make({
                'peoplename': peoplename,
                'time_overlap': time_overlap1,
                'mode': mode,
                'use_fix': use_fix,
                'auto_level': auto_level,
                'soft': soft,
                'low': low,
                'high': high
            })
    except Exception as e:
        return json.dumps(str(e))
    else:
        del allPeopleList[request.form['prepeoplename']][request.form['description']]
        allPeopleList[peoplename][data.get_description()] = {'data': data, 'active': activeState}
        return json.dumps("SUCCESS")

if __name__ == "__main__":
    app.run()
