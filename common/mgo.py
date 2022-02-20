import pymongo

mgo_client = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")
db = mgo_client["audio_win"]
col_user = db["user"]
col_channel = db["channel"]


def getClients():
    users = col_user.find()
    clients = {}
    for u in users:
        print("id:{} name:{} ip:{} port:{} level:{} channels:{}".format(u["_id"], u["name"], u["ip"], u["port"],
                                                                        u["level"], u["listening_channels"]))
        clients[str(u["_id"])] = {
            "name": u["name"],
            "ip": u["ip"],
            "port": u["port"],
            "level": u["level"]
        }

    return clients


def getChannels():
    channel_ret = col_channel.find()
    channels = {}
    for c in channel_ret:
        print("id:{} ip:{} port:{}".format(c["_id"], c["ip"], c["port"]))
        channels[str(c["_id"])] = {"ip": c["ip"], "port": c["port"]}

    return channels
