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
        self.users = {}


# 保存录音文件
def save_wav(path, file_name, datas):
    p = pyaudio.PyAudio()
    if not os.path.exists(path):
        os.makedirs(path)
    with wave.open(os.path.join(path, file_name), "wb") as f:
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
        self.mgo_client = None

    def start_channel(self, mgo_client):
        logging.info("start channel {}. addr: {}:{}".format(self.channel_id, self.ip, self.port))
        self.mgo_client = mgo_client
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.ip, self.port))
        self.channel_save = VoiceSaveInfo()

        while True:
            data, addr = s.recvfrom(2048)

            msg = my_udp.UdpMsg(msg=data)
            msg_body = json.loads(msg.getBody())

            # 通道消息
            if msg.msgType in [100]:
                uid_to = msg_body['from']
                now = datetime.now()
                if self.channel_save.start_time is None:
                    self.channel_save.start_time = now
                    threading.Thread(target=self.save_channel_file).start()
                self.channel_save.end_time = now
                # if uid_to not in self.channel_save.users:
                #     self.channel_save.users[uid_to] = {
                #         "start": now,
                #         "end": now,
                #     }
                # else:
                #     self.channel_save.users[uid_to]['end'] = now
                self.channel_save.voice_data_list.append(msg.getVoiceData())
                for uid_to in self.clients.keys():
                    # broadcast
                    if self.clients[uid_to]["ip"] == addr[0] and self.clients[uid_to]["port"] == addr[1]:
                        continue
                    try:
                        s.sendto(msg.getMsg(), (self.clients[uid_to]["ip"], self.clients[uid_to]["port"]))
                    except Exception as e:
                        logging.error(
                            "[channel] send to {}:{} err:{}".format(
                                self.clients[uid_to]["ip"], self.clients[uid_to]["port"], e))
            # 客户端私聊消息
            elif msg.msgType == 101:
                uid_to = msg_body['to']
                uid_from = msg_body['from']
                call_id = msg_body['call_id']
                now = datetime.now()

                if call_id not in self.phone_call_saves.keys():
                    self.phone_call_saves[call_id] = VoiceSaveInfo()
                if self.phone_call_saves[call_id].start_time is None:
                    self.phone_call_saves[call_id].start_time = now
                    threading.Thread(target=self.save_phone_call_file, args=(call_id,)).start()
                self.phone_call_saves[call_id].end_time = now
                if uid_from not in self.phone_call_saves[call_id].users:
                    self.phone_call_saves[call_id].users[uid_from] = {
                        "start": now,
                        "end": now,
                    }
                else:
                    self.phone_call_saves[call_id].users[uid_from]['end'] = now

                self.phone_call_saves[call_id].voice_data_list.append(msg.getVoiceData())
                try:
                    s.sendto(msg.getMsg(), (self.clients[uid_to]["ip"], self.clients[uid_to]["port"]))
                except Exception as e:
                    logging.error(
                        "[channel] send to {}:{} err:{}".format(
                            self.clients[uid_to]["ip"], self.clients[uid_to]["port"], e))

    def save_channel_file(self):
        logging.info("save_channel_file start save file.")
        while True:
            if self.channel_save.end_time and \
                    self.channel_save.start_time \
                    and (datetime.now() - self.channel_save.end_time).seconds > 5:

                voice_file_name = "{}-{}-{}.wav".format(self.channel_id,
                                                        self.channel_save.start_time.strftime("%H.%M.%S"),
                                                        self.channel_save.end_time.strftime("%H.%M.%S"))
                relative_dir = os.path.join("channel",
                                            self.channel_save.start_time.strftime('%Y%m/%d'))
                data = self.channel_save.voice_data_list
                record = {
                    "channel_id": self.channel_id,
                    "path": os.path.join(relative_dir, voice_file_name),
                    "st": self.channel_save.start_time,
                    "ed": self.channel_save.end_time,
                    "users": self.channel_save.users
                }

                self.channel_save = VoiceSaveInfo()

                # 存储文件
                save_wav(file_name=voice_file_name, path=os.path.join(self.storage_dir, relative_dir), datas=data)

                # 插入数据库
                try:
                    self.mgo_client.channel_detail.insert(record)
                except Exception as e:
                    logging.error("[mongo] update channel_detail: err:{}, data:{}".format(e, record))
                logging.info("save_channel_file file saved: {}".format(voice_file_name))
                return
            else:
                time.sleep(1)

    def save_phone_call_file(self, call_id):
        logging.info("save_phone_call_file start save file.")
        while True:
            if self.phone_call_saves[call_id].end_time and \
                    self.phone_call_saves[call_id].start_time and \
                    (datetime.now() - self.phone_call_saves[call_id].end_time).seconds > 5:
                voice_file_name = "{}-{}.wav".format(call_id,
                                                     self.phone_call_saves[call_id].start_time.strftime("%H.%M.%S"))
                relative_dir = os.path.join("call",
                                            self.phone_call_saves[call_id].start_time.strftime('%Y%m/%d'))
                data = self.phone_call_saves[call_id].voice_data_list
                record = {
                    "path": os.path.join(relative_dir, voice_file_name),
                    "st": self.phone_call_saves[call_id].start_time,
                    "ed": self.phone_call_saves[call_id].end_time,
                    "users": self.phone_call_saves[call_id].users
                }
                del self.phone_call_saves[call_id]

                # 存储文件
                save_wav(file_name=voice_file_name, path=os.path.join(self.storage_dir, relative_dir), datas=data)
                # 插入数据库
                try:
                    self.mgo_client.phone_detail.insert(record)
                except Exception as e:
                    logging.error("[mongo] update phone_detail: err:{}, data:{}".format(e, record))

                logging.info("save_phone_call_file file saved: {}".format(voice_file_name))
                return
            else:
                time.sleep(1)
