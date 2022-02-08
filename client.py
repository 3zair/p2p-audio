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
    def __init__(self, ip, port):
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

        self.init(ip, port)
        # udp
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.user["ip"], self.user["port"]))

        self.p = pyaudio.PyAudio()
        self.chunk_size = 1024  # 512
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

        self.RECORD_SECONDS = 10
        self.WAVE_OUTPUT_FILENAME = "output"

        # start threads
        threading.Thread(target=self.receive_server_data).start()
        self.playing_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate,
                                          output=True,
                                          frames_per_buffer=self.chunk_size)
        self.record_frames = []
        self.play_frames = []

        threading.Thread(target=self.play).start()

    def play(self):
        while True:
            if len(self.play_frames) > 0:
                pfs = self.play_frames.pop()
                for pf in pfs:
                    print("play{}".format(pf))
                    self.playing_stream.write(pf)

    def choose_channel(self, channel_id):
        logging.info("choose_channel {}".format(channel_id))
        msg = my_udp.udpMsg(msgType=200, t=time.time(),
                            body=json.dumps({"uid": self.user["id"], "channel_id": channel_id}))
        self.s.sendto(msg.getMsg(), self.getChannel())
        t = time.time()
        while self.CurChannel != channel_id:
            if time.time() - t > 1:
                return "Time out"
            if "cur_uid" in self.SetChannelRet:
                return "当前通道被{}占用".format(self.ClientsInfo[self.SetChannelRet["cur_uid"]])
        return True

    def cancel_channel(self, channel_id):
        logging.info("cancel_channel {}".format(channel_id))
        msg = my_udp.udpMsg(msgType=201, t=time.time(),
                            body=json.dumps({"uid": self.user["id", "channel_id":channel_id]}))
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
                msg = my_udp.udpMsg(msg=data)
                msg_body = json.loads(msg.getBody())
                # logging.info(
                #     "receive header: {} body:{}".format(msg.headers, msg_body))
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
                if msg.msgType == 100 and msg_body["channel_id"] in self.user["listening_channels"]:
                    #logging.info("【监听信道】 播放，name: {}, channel:{}".format(msg_body["from"], msg_body["channel_id"]))
                    channel_orders.append(msg.MsgTime)
                    channel_buffer[msg.MsgTime] = msg.getVoiceData()
                    if len(channel_orders) == 20:
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
        recording_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate,
                                       input=True,
                                       frames_per_buffer=self.chunk_size)
        while self.VoiceRecordFlag:
            # 打开一个数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
            data = recording_stream.read(1024, exception_on_overflow=False)
            self.record_frames.append(data)
        recording_stream.close()
        return

    # 将声音数据发送到通道上 100
    def start_send_to_channel(self, channel_id):
        logging.info("start_send_to_channel {}".format(channel_id))

        self.ChannelFlag = True
        t = threading.Thread(target=self.send_voice_data, args=("channel", channel_id))
        t.start()

    # 停止向当前的通道发送数据
    def stop_send_to_channel(self):
        logging.info("stop_send_to_channel {}".format(self.CurChannel))
        self.ChannelFlag = False
        self.cancel_channel(self.CurChannel)

    # 将声音数据发送到客户端上 101
    def send_to_user(self, uid):
        self.UserFlag = True
        t = threading.Thread(target=self.send_voice_data, args=("user", uid))
        t.setDaemon(True)
        t.start()

    def stop_send_to_user(self):
        logging.info("stop_send_to_user")
        self.UserFlag = False

    def send_voice_data(self, type, to_id):
        logging.info("start_send_voice_data")
        if type == "channel":
            while self.ChannelFlag:
                if len(self.record_frames) > 0:
                    try:
                        body = {"from": self.user["id"], "channel_id": self.CurChannel}
                        msg = my_udp.udpMsg(msgType=100, t=time.time(), body=json.dumps(body),
                                            voiceData=self.record_frames.pop())
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
                        msg = my_udp.udpMsg(msgType=101, t=time.time(), body=json.dumps(body),
                                            voiceData=self.record_frames.pop())
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
            logging.info(
                "client id:{} name:{} ip:{} port:{} level:{} channels:{}".format(u["_id"], u["name"], u["ip"],
                                                                                 u["port"],
                                                                                 u["level"], u["listening_channels"]))
        channel_ret = self.col_channel.find()
        for c in channel_ret:
            logging.info(
                "channel id:{} ip:{} port:{}".format(c["_id"], c["ip"], c["port"]))
            self.Channels[str(c["_id"])] = {"port": c["port"], "ip": c["ip"]}

    def getChannel(self):
        channel_id = random.choice(list(self.Channels.keys()))
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
client = ChatClient(socket.gethostbyname(socket.gethostname()), 8002)
ret = client.choose_channel("1")
if not ret:
    logging.error("choose_channel err:{}".format(ret))

client.start_record_voice_data()
client.start_send_to_channel("1")
