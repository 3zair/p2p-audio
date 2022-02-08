# 暂时没用
from flask import Flask, request, jsonify
import mgo

app = Flask(__name__)

Channels = mgo.getChannels()
Clients = mgo.getClients()


# 判断channel是否可用
@app.route("/channel/occupy", methods=['POST'])
def hello_world():
    channel_id = request.form.get("channel_id")
    uid = request.args.get("uid")
    if "user" not in Channels["channel_id"]:
        Channels["channel_id"]["user"] = uid
        return jsonify({"code": 200, "msg": "信道占用成功"})
    elif Clients[Channels["channel_id"]["user"]]["level"] < Clients["uid"]["level"]:
        pass
    else:
        return jsonify({"code": 201, "msg": "已被更高等级用户占用", "cur_id": Channels["channel_id"]["user"]})
