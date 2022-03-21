import json
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


# 录音文件信息
class VoiceSaveInfo:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.voice_data_list = []


# 保存录音文件
def save_wav(relative_dir, file_name, datas):
    p = pyaudio.PyAudio()
    if not os.path.exists(relative_dir):
        os.makedirs(relative_dir)
    with wave.open(os.path.join(relative_dir, file_name), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        f.setframerate(4000)
        f.writeframes(b''.join(datas))
        f.close()


class ChatServer:

    def __init__(self, channel_id, ip, port, clients, storage_dir):
        self.channel_id = channel_id
        self.ip = ip
        self.port = port
        self.clients = clients
        self.storage_dir = storage_dir
        self.channel_save = None
        self.phone_call_saves = {}

    def start_channel(self):
        logging.info("start channel {}. addr: {}:{}".format(self.channel_id, self.ip, self.port))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.ip, self.port))
        self.channel_save = VoiceSaveInfo()

        while True:
            # 接收来自客户端的数据,使用recv from
            data, addr = s.recvfrom(2048)
            msg = my_udp.UdpMsg(msg=data)

            if msg.msgType in [100]:
                if self.channel_save.start_time is None:
                    self.channel_save.start_time = datetime.now()
                    threading.Thread(target=self.save_channel_file).start()
                self.channel_save.end_time = datetime.now()
                self.channel_save.voice_data_list.append(msg.getVoiceData())
                for uid in self.clients.keys():
                    # broadcast
                    if self.clients[uid]["ip"] == addr[0] and self.clients[uid]["port"] == addr[1]:
                        continue
                    try:
                        s.sendto(msg.getMsg(), (self.clients[uid]["ip"], self.clients[uid]["port"]))
                    except Exception as e:
                        logging.error(
                            "send to {}:{},err:{}".format(self.clients[uid]["ip"], self.clients[uid]["port"], e))

            else:
                if msg.msgType == 101:
                    msg_body = json.loads(msg.getBody())
                    uid = msg_body['to']
                    call_id = msg_body['call_id']
                    if call_id not in self.phone_call_saves.keys():
                        self.phone_call_saves[call_id] = VoiceSaveInfo()
                    if self.phone_call_saves[call_id].start_time is None:
                        self.phone_call_saves[call_id].start_time = datetime.now()
                        threading.Thread(target=self.save_phone_call_file, args=(call_id,)).start()
                    self.phone_call_saves[call_id].end_time = datetime.now()
                    self.phone_call_saves[call_id].voice_data_list.append(msg.getVoiceData())

                    logging.info("from:{} to:{} call_id:{} channel:{}".format(msg_body['from'], uid, call_id,
                                                                              msg_body['channel_id']))
                    try:
                        s.sendto(msg.getMsg(), (self.clients[uid]["ip"], self.clients[uid]["port"]))
                    except Exception as e:
                        logging.error(
                            "send to {}:{},err:{}".format(self.clients[uid]["ip"], self.clients[uid]["port"], e))

    def save_channel_file(self):
        logging.info("start save file.")
        while True:
            if self.channel_save.end_time and self.channel_save.start_time and (
                    datetime.now() - self.channel_save.end_time).seconds > 5:
                voice_file_name = "channel_{}-{}-{}.wav".format(self.channel_id,
                                                                self.channel_save.start_time.strftime("%H.%M.%S"),
                                                                self.channel_save.end_time.strftime("%H.%M.%S"))
                data = self.channel_save.voice_data_list
                self.channel_save.start_time = None
                self.channel_save.end_time = None
                self.channel_save.voice_data_list = []
                relative_dir = os.path.join(self.storage_dir, "channel", datetime.now().strftime('%Y%m/%d'))
                save_wav(file_name=voice_file_name, relative_dir=relative_dir, datas=data)

                logging.info("save file {}".format(voice_file_name))
                # TODO 更新数据库
                return
            else:
                time.sleep(1)

    def save_phone_call_file(self, call_id):
        logging.info("start save file.")
        while True:
            if self.phone_call_saves[call_id].end_time and self.phone_call_saves[call_id].start_time and (
                    datetime.now() - self.phone_call_saves[call_id].end_time).seconds > 5:
                voice_file_name = "phone_{}-{}.wav".format(call_id, self.phone_call_saves[call_id].start_time.strftime(
                    "%H.%M.%S"))
                data = self.phone_call_saves[call_id].voice_data_list
                del self.phone_call_saves[call_id]

                relative_dir = os.path.join(self.storage_dir, "call", datetime.now().strftime('%Y%m/%d'))
                save_wav(file_name=voice_file_name, relative_dir=relative_dir, datas=data)
                logging.info("save file {}".format(voice_file_name))

                # TODO 更新数据库
                return
            else:
                time.sleep(1)
