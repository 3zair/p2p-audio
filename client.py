import socket
import threading
import my_udp
import logging
import json
import pymongo
import struct
import random
import pyaudio
import time


class ChatClient:
    def __init__(self):
        db = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")["audio"]
        self.col_user = db["user"]
        self.col_channel = db["channel"]

        """
        当前用户的信息
        keys：
            id: uid
            name: 称呼
            ip: IP地址
            port: udp端口
            level: 等级
            listening_channels: [channel_id]  所监听的通道
            listening_clients: [uid] 所监听的客户端
        """
        self.user = {}

        self.ClientsInfo = {}  # 客户端的信息
        self.Channels = {}  # channel的信息

        # 消息发送结束标识
        self.ChannelFlag = False
        self.UserFlag = False
        self.VoiceRecordFlag = False

        # 发消息
        self.CurClient = None  # 当前选择通话的用户
        self.CurChannel = None  # 当前占用的通道
        self.SetChannelRet = {}

        # udp
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.user["ip"], self.user["port"]))

        # start threads
        threading.Thread(target=self.receive_server_data).start()
        self.record_frames = []
        self.play_frames = []

    def setChannel(self, channel_id):
        msg = my_udp.udpMsg(200, json.dumps({"uid": self.user["id", "channel_id":channel_id]}))
        self.s.sendto(msg.getMsg(), self.getChannel())
        t = time.time()
        while self.CurChannel != channel_id:
            if time.time() - t > 1:
                return "Time out"
            if "cur_uid" in self.SetChannelRet:
                return "当前通道被{}占用".format(self.ClientsInfo[self.SetChannelRet["cur_uid"]])
        return True

    def cancelChannel(self, channel_id):
        msg = my_udp.udpMsg(201, json.dumps({"uid": self.user["id", "channel_id":channel_id]}))
        self.s.sendto(msg.getMsg(), self.getChannel())
        t = time.time()
        while self.CurChannel is None:
            if time.time() - t > 1:
                return "Time out"
        self.ChannelFlag = False
        return True

    # 监听数据
    def receive_server_data(self):
        channel_buffer = {}
        channel_orders = []

        client_buffer = {}
        client_orders = []
        while True:
            try:
                data, _server = self.s.recvfrom(4096)
                msg = my_udp.udpMsg(voiceDataLen=len("data"), msg=data)
                msg_body = json.loads(msg.getBody())
                logging.info(
                    "receive form {}, name: {}, channel:{}".format(msg_body["from"], self.ClientsInfo[msg_body["from"]],
                                                                   msg_body["channel"]))
                # 占用通道请求的结果
                if msg.msgType == 200:
                    if msg_body["ret"]:
                        self.CurChannel = msg_body["channel_id"]
                    else:
                        self.SetChannelRet["cur_uid"] = msg_body["user"]
                elif msg.msgType == 201:
                    if msg_body["ret"]:
                        self.CurChannel = None
                # TODO 获取当前监听的的客户端,放入播放队列
                # if msg.msgType == 101 and msg_body["from"] in User["listening_clients"]:
                #     logging.info("【监听客户端】播放，name: {}".format(msg_body["from"]))
                #
                #     client_orders.append(msg.MsgTime)
                #     client_buffer[msg.MsgTime] = msg.getVoiceData()
                #     if len(client_orders) == 20:
                #         client_orders.sort()
                #         for t in client_orders:
                #             self.play_frames.append(client_buffer[t])
                #     client_orders = []
                #     client_buffer = {}

                # TODO 是当前监听的信道，放入播放队列
                if msg.msgType == 100 and msg_body["channel"] in self.user["listening_channels"]:
                    logging.info("【监听信道】 播放，name: {}, channel:{}".format(msg_body["from"], msg_body["channel"]))
                    channel_orders.append(msg.MsgTime)
                    channel_buffer[msg.MsgTime] = msg.getVoiceData()
                    if len(channel_orders) == 20:
                        channel_orders.sort()
                        for t in channel_orders:
                            # 放入播放队列
                            self.play_frames.append(channel_buffer[t])
                    channel_orders = []
                    channel_buffer = {}
            except Exception as e:
                logging.error("receive_server_data err {}".format(e))

    # 开始收取声音数据
    def start_record_voice_data(self):
        self.VoiceRecordFlag = True
        threading.Thread(target=self.record_voice_data).start()

    # 停止收取声音数据
    def stop_record_voice_data(self):
        self.VoiceRecordFlag = False

    # 收取声音数据
    def record_voice_data(self):
        while self.VoiceRecordFlag:
            # TODO
            self.record_frames.append("voice_data")
        return

    # 将声音数据发送到通道上 100
    def send_to_channel(self, channel_id):
        self.ChannelFlag = True
        threading.Thread(target=self.send_voice_data, args=("channel", channel_id)).start()

    # 停止向当前的通道发送数据
    def stop_send_to_channel(self):
        self.ChannelFlag = False
        self.cancelChannel(self.CurChannel)

    # 将声音数据发送到客户端上 101
    def send_to_user(self, uid):
        self.UserFlag = True
        threading.Thread(target=self.send_voice_data, args=("user", uid)).start()

    def stop_send_to_user(self):
        self.UserFlag = False

    def send_voice_data(self, type, to_id):
        if type == "channel":
            while self.ChannelFlag:
                if len(self.record_frames) > 0:
                    try:
                        body = {"from": self.user["id"]}
                        msg = my_udp.udpMsg(100, json.dumps(body), voiceData=self.record_frames.pop())
                        self.s.sendto(msg.getMsg(),
                                      (self.Channels[to_id]["ip"], self.Channels[to_id]["port"]))
                    except Exception as e:
                        logging.error("send_data_to_server err: {}".format(e))
        elif type == "user":
            while self.UserFlag:
                if len(self.record_frames) > 0:
                    try:
                        # TODO
                        body = {"from": self.user["id"]}
                        msg = my_udp.udpMsg(101, json.dumps(body), voiceData=self.record_frames.pop())
                        self.s.sendto(msg.getMsg(),
                                      (self.ClientsInfo[to_id]["ip"], self.ClientsInfo[to_id]["port"]))
                    except Exception as e:
                        logging.error("send_data_to_user err: {}".format(e))

    def init(self, ip, port):
        # TODO read from conf
        self.user["ip"] = ip
        self.user["port"] = port

        users = self.col_user.find()
        for u in users:
            if self.user["ip"] == u["ip"] and self.user["port"] == u["port"]:
                self.user["name"] = u["name"]
                self.user["id"] = u["_id"]
                self.user["level"] = u["level"]
                self.user["listening_channels"] = [] if "channels" not in u else u["listening_channels"][:]
                self.user["listening_clients"] = [] if "listening_clients" not in u else u["listening_clients"][:]
            else:
                self.ClientsInfo[u["_id"]] = {
                    "name": u["name"],
                    "ip": u["ip"],
                    "port": u["port"],
                    "level": u["level"],
                }
            logging.info(
                "client id:{} name:{} ip:{} port:{} level:{} channels:{}".format(u["_id"], u["name"], u["ip"],
                                                                                 u["port"],
                                                                                 u["level"], u["channels"]))
        channel_ret = self.col_channel.find()
        for c in channel_ret:
            logging.info(
                "channel id:{} ip:{} port:{}".format(c["_id"], c["ip"], c["port"]))
            self.Channels[c["_id"]] = {"port": c["port"], "ip": c["ip"]}

    def getChannel(self):
        channel_id = self.Channels[random.randint(0, len(self.Channels) - 1)]
        return self.Channels[channel_id]["ip"], self.Channels[channel_id]["port"]

    # 设置使用的信道
    def setCurChannel(self, channel_id):
        self.CurChannel = channel_id
        return

    # 开始听某个客户端的消息
    def addListening_client(self, uid):
        self.user["listening_clients"].append(uid)
        self.col_user.update_one({"_id": self.user["id"]}, {"$addToSet": {"listening_clients": uid}})
        return

    def delListening_client(self, uid):
        self.user["listening_clients"].remove(uid)
        self.col_user.update_one({"_id": self.user["id"]}, {"$pull": {"listening_clients": uid}})

        return

    # 开始监听某个channel
    def addListening_channel(self, channel_id):
        self.user["listening_channels"].append(self, channel_id)
        self.col_user.update_one({"_id": self.user["id"]}, {"$addToSet": {"listening_channels": channel_id}})

        return

    def delListening_channel(self, channel_id):
        self.user["listening_channels"].remove(channel_id)
        self.col_user.update_one({"_id": self.user["id"]}, {"$pull": {"listening_channels": channel_id}})

        return


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ChatClient()
