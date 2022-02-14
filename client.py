import socket
import threading

import bson

import my_udp
import logging
import json
import pymongo
import random
import pyaudio
import time


class ChatClient:
    def __init__(self, ip, port):
        db = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")["audio_office"]
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
        self.ExitFlag = False

        # 发消息
        self.CurClient = None  # 当前选择通话的用户
        self.CurChannel = None  # 当前占用的通道
        self.SetChannelRet = {}

        self.Init(ip, port)

        # udp
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.user["ip"], self.user["port"]))

        self.p = pyaudio.PyAudio()
        self.chunk_size = 512  # 512
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.rate = 16000
        self.RECORD_SECONDS = 10
        self.WAVE_OUTPUT_FILENAME = "output"
        # start threads
        threading.Thread(target=self.receive_server_data).start()
        self.playing_stream = self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                                          output=True,
                                          frames_per_buffer=self.chunk_size)
        self.record_frames = []
        self.play_frames = []

        threading.Thread(target=self.play).start()

    def Init(self, ip, port):
        # TODO read from conf
        self.user["ip"] = ip
        self.user["port"] = port

        users = self.col_user.find()
        for u in users:
            if self.user["ip"] == u["ip"] and self.user["port"] == u["port"]:
                self.user["name"] = u["name"]
                self.user["id"] = str(u["_id"])
                self.user["level"] = u["level"]
                self.user["listening_channels"] = [] if "listening_channels" not in u else u["listening_channels"][:]
                self.user["listening_clients"] = [] if "listening_clients" not in u else u["listening_clients"][:]
            else:
                self.ClientsInfo[str(u["_id"])] = {
                    "name": u["name"],
                    "ip": u["ip"],
                    "port": u["port"],
                    "level": u["level"],
                }
            logging.info("client id:{} name:{} ip:{} port:{} level:{} channels:{}".format(
                u["_id"], u["name"], u["ip"], u["port"], u["level"], u["listening_channels"]))
        channel_ret = self.col_channel.find()
        for c in channel_ret:
            logging.info(
                "channel id:{} ip:{} port:{}".format(c["_id"], c["ip"], c["port"]))
            self.Channels[str(c["_id"])] = {"port": c["port"], "ip": c["ip"]}

    # 监听数据
    def receive_server_data(self):
        channel_buffer, client_buffer = {}, {}
        channel_orders, client_orders = [], []

        while not self.ExitFlag:
            try:
                data, _server = self.s.recvfrom(1500)
                msg = my_udp.udpMsg(msg=data)
                msg_body = json.loads(msg.getBody())

                # 占用通道请求的结果
                if msg.msgType == 200:
                    if msg_body["ret"]:
                        self.CurChannel = msg_body["channel_id"]
                    else:
                        self.SetChannelRet["cur_uid"] = msg_body["user"]
                # 取消占用通道请求的结果
                elif msg.msgType == 201:
                    if msg_body["ret"]:
                        self.CurChannel = None

                # TODO 获取当前监听的的客户端,放入播放队列
                # if msg.msgType == 101 and msg_body["from"] in User["listening_clients"]:
                #     logging.info("【监听客户端】播放，name: {}".format(msg_body["from"]))
                #
                #     client_orders.append(msg.msgNum)
                #     client_buffer[msg.msgNum] = msg.getVoiceData()
                #     if len(client_orders) == 20:
                #         client_orders.sort()
                #         for t in client_orders:
                #             self.play_frames.append(client_buffer[t])
                #     client_orders = []
                #     client_buffer = {}

                # TODO 是当前监听的信道，放入播放队列
                if msg.msgType == 100 and msg_body["channel_id"] in self.user["listening_channels"]:
                    # logging.info("【监听信道】 播放，name: {}, channel:{} num:{}".format(
                    #     msg_body["from"], msg_body["channel_id"], msg.msgNum))
                    channel_orders.append(msg.msgNum)
                    channel_buffer[msg.msgNum] = msg.getVoiceData()
                    if len(channel_orders) == 10:
                        channel_orders.sort()
                        play_frame_body = []
                        for t in channel_orders:
                            # 放入播放队列
                            play_frame_body.append(channel_buffer[t])
                        self.play_frames.append(play_frame_body)
                        channel_orders = []
                        channel_buffer = {}
            except Exception as e:
                logging.error("receive_server_data err {}".format(e))

        logging.info("stop receive_server_data.")

    # 请求占用channel
    def choose_channel(self, channel_id):
        logging.info("choose_channel {} {}".format(channel_id, self.user))
        msg = my_udp.udpMsg(msgType=200,
                            body=json.dumps({"uid": self.user["id"], "channel_id": channel_id}))
        self.s.sendto(msg.getMsg(), self.getChannel())
        t = time.time()
        while self.CurChannel != channel_id:
            if time.time() - t > 1:
                return "Time out"
            if "cur_uid" in self.SetChannelRet:
                return "当前通道被{}占用".format(self.ClientsInfo[self.SetChannelRet["cur_uid"]])
        return True

    # 取消占用channel
    def cancel_channel(self, channel_id):
        logging.info("cancel_channel {}".format(channel_id))
        msg = my_udp.udpMsg(msgType=201,
                            body=json.dumps({"uid": self.user["id"], "channel_id": channel_id}))
        self.s.sendto(msg.getMsg(), self.getChannel())
        t = time.time()
        while self.CurChannel is not None:
            if time.time() - t > 1:
                return "Time out"
        self.ChannelFlag = False
        return True

    # 开始收取声音数据
    def start_record_voice_data(self):
        logging.info("start_record_voice_data")
        self.VoiceRecordFlag = True
        t = threading.Thread(target=self.record_voice_data)
        t.start()

    # 停止收取声音数据
    def stop_record_voice_data(self):
        logging.info("stop_record_voice_data")

        self.VoiceRecordFlag = False

    # 收取声音数据
    def record_voice_data(self):
        recording_stream = self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                                       input=True,
                                       frames_per_buffer=self.chunk_size)
        while not self.ExitFlag and self.VoiceRecordFlag:
            # 打开一个数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
            data = recording_stream.read(self.chunk_size, exception_on_overflow=False)
            self.record_frames.append(data)
            time.sleep(0.8 * self.chunk_size / self.rate)
            if len(self.record_frames) > 100:
                # 防止按下按钮开始监听了但是发送端出现问题，不能发送消息，造成内存溢出
                self.record_frames = []
        recording_stream.close()
        logging.info("stop send_voice_data.")
        return

    # 将声音数据发送到通道上 100
    def start_send_to_channel(self):
        logging.info("start_send_to_channel {}".format(self.CurChannel))

        self.ChannelFlag = True
        threading.Thread(target=self.send_voice_data, args=("channel", self.CurChannel)).start()

    # 停止向当前的通道发送数据
    def stop_send_to_channel(self):
        logging.info("stop_send_to_channel")
        self.ChannelFlag = False

    # 将声音数据发送到客户端上 101
    def send_to_user(self, uid):
        self.UserFlag = True
        threading.Thread(target=self.send_voice_data, args=("user", uid)).start()

    # 停止声音数据发送到客户端上 101
    def stop_send_to_user(self):
        logging.info("stop_send_to_user")
        self.UserFlag = False

    def send_voice_data(self, type, to_id):
        logging.info("start_send_voice_data")
        # 发送到通道
        if type == "channel":
            num = 0
            while not self.ExitFlag and self.ChannelFlag:
                if len(self.record_frames) > 0:
                    try:
                        body = {"from": self.user["id"], "channel_id": to_id}
                        msg = my_udp.udpMsg(msgType=100, num=num, body=json.dumps(body),
                                            voiceData=self.record_frames.pop())
                        self.s.sendto(msg.getMsg(),
                                      (self.Channels[to_id]["ip"], self.Channels[to_id]["port"]))
                        num += 1
                        # 最大标号100000
                        if num == 100000:
                            num = 0
                    except Exception as e:
                        logging.error("send_data_to_server err: {}".format(e))
        # 发送给用户
        elif type == "user":
            num = 0
            while not self.ExitFlag and self.UserFlag:
                if len(self.record_frames) > 0:
                    try:
                        # TODO
                        body = {"from": self.user["id"]}
                        msg = my_udp.udpMsg(msgType=101, num=num, body=json.dumps(body),
                                            voiceData=self.record_frames.pop())
                        self.s.sendto(msg.getMsg(),
                                      (self.ClientsInfo[to_id]["ip"], self.ClientsInfo[to_id]["port"]))
                        num += 1
                        # 最大标号100000
                        if num == 100000:
                            num = 0
                    except Exception as e:
                        logging.error("send_data_to_user err: {}".format(e))
        logging.info("stop send_voice_data.")

    # 播放声音
    def play(self):
        while not self.ExitFlag:
            if len(self.play_frames) > 0:
                pfs = self.play_frames.pop()
                for pf in pfs:
                    self.playing_stream.write(pf)
                    time.sleep(0.8 * self.chunk_size / self.rate)
        self.playing_stream.close()
        logging.info("stop play.")

    def getChannel(self):
        channel_id = random.choice(list(self.Channels.keys()))
        return self.Channels[channel_id]["ip"], self.Channels[channel_id]["port"]

    # 设置使用的信道
    def setCurChannel(self, channel_id):
        logging.info("")
        self.CurChannel = channel_id
        return

    # 开始听某个客户端的消息
    def addListening_client(self, uid):
        self.user["listening_clients"].append(uid)
        self.col_user.update_one({"_id": bson.ObjectId(self.user["id"])}, {"$addToSet": {"listening_clients": uid}})
        return

    def delListening_client(self, uid):
        self.user["listening_clients"].remove(uid)
        self.col_user.update_one({"_id": bson.ObjectId(self.user["id"])}, {"$pull": {"listening_clients": uid}})

        return

    # 开始监听某个channel
    def addListening_channel(self, channel_id):
        logging.info("addListening_channel {}".format(channel_id))
        self.user["listening_channels"].append(channel_id)
        self.col_user.update_one({"_id": bson.ObjectId(self.user["id"])},
                                 {"$addToSet": {"listening_channels": channel_id}})

        return

    def delListening_channel(self, channel_id):
        logging.info("delListening_channel {}".format(channel_id))
        self.user["listening_channels"].remove(channel_id)
        self.col_user.update_one({"_id": bson.ObjectId(self.user["id"])}, {"$pull": {"listening_channels": channel_id}})

        return

    def exit(self):
        self.ExitFlag = True
        self.s.close()
