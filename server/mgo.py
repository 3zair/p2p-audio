import pymongo


class Mgo:
    def __init__(self, url, db_name):
        self.col_user = None
        self.client = None
        self.col_channel = None

        self.db_url = url
        self.db_name = db_name
        self.connect()

    def connect(self):
        self.client = pymongo.MongoClient(self.db_url)
        db = self.client[self.db_name]
        self.col_channel = db["channel"]
        self.col_user = db['user']

    def get_channels(self):
        channel_ret = self.col_channel.find()
        channels = {}
        for c in channel_ret:
            channels[str(c["_id"])] = {"ip": c["ip"], "port": c["port"], "status": c["status"]}

        return channels

    def get_clients(self):
        users = self.col_user.find()
        clients = {}
        for u in users:
            clients[str(u["_id"])] = {"name": u["name"], "ip": u["ip"], "port": u["port"]}

        return clients
