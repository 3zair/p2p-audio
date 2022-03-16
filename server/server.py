import os
import socket
import logging
import threading
import time
import wave
from datetime import datetime

import pyaudio
import my_udp

CONF_PATH = os.path.join(os.getcwd(), "conf.yml")


class ChatServer:
    def __init__(self, channel_id, ip, port, clients, storage_dir):
        self.channel_id = channel_id
        self.ip = ip
        self.port = port
        self.clients = clients
        self.storage_dir = storage_dir
        self.start_time = None
        self.end_time = None
        self.voice_data_list = []

    def start_channel(self):
        logging.info("start channel {}. addr: {}:{}".format(self.channel_id, self.ip, self.port))
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.ip, self.port))

        while True:
            # 接收来自客户端的数据,使用recv from
            data, addr = s.recvfrom(2048)
            msg = my_udp.UdpMsg(msg=data)
            # logging.info(
            #     "receive from {}, type:{} num: {} body:{} start:{}".format(addr, msg.msgType, msg.msgNum, msg.getBody(),
            #                                                                self.start_time))
            if msg.msgType in [100]:

                if self.start_time is None:
                    self.start_time = datetime.now()
                    threading.Thread(target=self.save_channel_file).start()
                self.end_time = datetime.now()
                self.voice_data_list.append(msg.getVoiceData())
                for uid in self.clients.keys():
                    # broadcast
                    if self.clients[uid]["ip"] == addr[0] and self.clients[uid]["port"] == addr[1]:
                        continue
                    try:
                        s.sendto(msg.getMsg(), (self.clients[uid]["ip"], self.clients[uid]["port"]))
                    except Exception as e:
                        logging.error(
                            "send to {}:{},err:{}".format(self.clients[uid]["ip"], self.clients[uid]["port"], e))

    def save_channel_file(self):
        logging.info("start save file.")
        while True:
            if self.end_time is not None and self.start_time is not None and (datetime.now() - self.end_time).seconds > 5:
                voice_file_name = "channel_{}-{}-{}.wav".format(self.channel_id, self.start_time.strftime("%H.%M.%S"),
                                                        self.end_time.strftime("%H.%M.%S"))
                data = self.voice_data_list
                self.start_time = None
                self.end_time = None
                self.voice_data_list = []
                self.save_wav(file_name=voice_file_name, datas=data)

                logging.info("save file {}".format(voice_file_name))
                # TODO 更新数据库
                return
            else:
                time.sleep(1)

    def save_wav(self, file_name, datas):
        dir = os.path.join(self.storage_dir, datetime.now().strftime('%Y%m/%d'))
        p = pyaudio.PyAudio()
        if not os.path.exists(dir):
            os.makedirs(dir)
        with wave.open(os.path.join(dir, file_name), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            f.setframerate(4000)
            f.writeframes(b''.join(datas))
            f.close()

        # # 200 占用通道请求
        # if msg.msgType == 200:
        #     body = json.loads(msg.getBody())
        #     if body["channel_id"] in self.channels:
        #         if "cur_user" not in self.channels[body["channel_id"]] or \
        #                 self.channels[body["channel_id"]]["cur_user"] is None or \
        #                 self.channels[body["channel_id"]]["cur_user"] == body["uid"]:
        #
        #             # 占用成功
        #             self.channels[body["channel_id"]]["cur_user"] = body["uid"]
        #             ret_msg = my_udp.UdpMsg(msgType=200,
        #                                     body=json.dumps({"ret": True, "channel_id": body["channel_id"]}))
        #             s.sendto(ret_msg.getMsg(), addr)
        #         else:
        #             # 当前channel已被占用，返回失败
        #             ret_msg = my_udp.UdpMsg(msgType=200, body=json.dumps(
        #                 {"ret": False, "cur_uid": self.channels[body["channel_id"]]["cur_user"]}),
        #                                     voiceData="")
        #             s.sendto(ret_msg.getMsg(), addr)
        #     else:
        #         logging.error("invalid channel_id: {}".format(body["channel_id"]))
        #
        # # 201 释放通道请求
        # elif msg.msgType == 201:
        #     body = json.loads(msg.getBody())
        #     if body["channel_id"] in self.channels:
        #         logging.error(self.channels[body["channel_id"]])
        #         if "cur_user" in self.channels[body["channel_id"]] and \
        #                 self.channels[body["channel_id"]]["cur_user"] == body["uid"]:
        #
        #             # 释放成功
        #             self.channels[body["channel_id"]]["cur_user"] = None
        #             ret_msg = my_udp.UdpMsg(msgType=201, body=json.dumps({"ret": True}),
        #                                     voiceData="")
        #             s.sendto(ret_msg.getMsg(), addr)
        #         else:
        #             logging.warning(
        #                 "释放通道失败 用户ID或者通道ID错误: uid:{} channel_id:{}".format(body["uid"], body["channel_id"]))
        #             # 当前用户已不再占用当前通道
        #             ret_msg = my_udp.UdpMsg(msgType=200, body=json.dumps({"ret": True}),
        #                                     voiceData="")
        #             s.sendto(ret_msg.getMsg(), addr)
        #     else:
        #         logging.error("invalid channel_id: {}".format(body["channel_id"]))
