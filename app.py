import json

from flask import Flask, render_template,request

from pyecharts import options as opts
from pyecharts.charts import Bar


app = Flask(__name__, static_folder="templates")

#name 下面加入description 不写入就默认 写入就修改

Param = {}
#user(zy) ->{
#   description(“zy soft:10 low:......”) -> {
#
#   },
# }

def bar_base() -> Bar:
    c = (
        Bar()
        .add_xaxis(["param1", "param2", "param3"])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
    )
    for i in Param:
        if Param[i]["active"] == 1 :
            c.add_yaxis(i, [ Param[i]["param1"],Param[i]["param2"],Param[i]["param3"] ] )
    return c


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bootstrap")
def bootstrap():
    return render_template("bootstrap.html", param = Param)

@app.route("/barChart")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()

@app.route("/changeActive/<name>")
def change_active(name):
    if(Param[name]['active'] == 0):
        Param[name]['active'] = 1
    else:
        Param[name]['active'] = 0
    c = bar_base()
    return c.dump_options_with_quotes()

@app.route("/deleteMember/<name>")
def delete_member(name):
    del Param[name]
    c = bar_base()
    return c.dump_options_with_quotes()

@app.route("/searchMember/<name>")
def search_member(name):
    c = json.dumps(Param[name])
    return c

@app.route("/setMember",methods=['POST', 'GET'])
def set_member():
    Param[request.args['name']] = {
        'param1': request.args['param1'],
        'param2': request.args['param2'],
        'param3': request.args['param3'],
        'active': 1
    }
    return render_template("bootstrap.html", param = Param)

@app.route("/changeMember",methods=['POST','GET'])
def change_member():
    Param[request.args['name']] = {
        'param1': request.args['param1'],
        'param2': request.args['param2'],
        'param3': request.args['param3'],
        'active': 1
    }
    return render_template("bootstrap.html", param=Param)

if __name__ == "__main__":
    app.run()