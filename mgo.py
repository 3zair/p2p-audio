import pymongo


def getClients():
    myclient = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")
    # db = myclient["whu_yjy"]
    db = myclient["audio_office"]
    col_user = db["user"]
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
    myclient = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")
    # db = myclient["whu_yjy"]
    db = myclient["audio_office"]
    col_channel = db["channel"]
    channel_ret = col_channel.find()
    channels = {}
    for c in channel_ret:
        print("id:{} ip:{} port:{}".format(c["_id"], c["ip"], c["port"]))
        channels[str(c["_id"])] = {"ip": c["ip"], "port": c["port"]}

    return channels
