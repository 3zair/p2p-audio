import socket
import my_udp
import json
import logging
import mgo
import threading

class ChatServer:
    def __init__(self):
        # init channels
        self.channels = mgo.getChannels()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        for channel_id in self.channels.keys():
            threading.Thread(target=self.serverStart,
                             args=(channel_id, self.channels[channel_id]["ip"],
                                   self.channels[channel_id]["port"])).start()

    def serverStart(self, channel_id, ip, port):
        # 建立IPv4,UDP的socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口：
        s.bind((ip, port))

        # 不需要开启listen，直接接收所有的数据
        print('Bind UDP on {}'.format(port))

        clients = mgo.getClients()
        while True:
            # 接收来自客户端的数据,使用recv from
            data, addr = s.recvfrom(2048)
            msg = my_udp.udpMsg(msg=data)
            logging.info("receive from {}, type:{} num: {} body:{}"
                         .format(addr, msg.msgType, msg.msgNum, msg.getBody()))

            if msg.msgType in [100, 101]:
                for uid in clients.keys():
                    # broadcast
                    if clients[uid]["ip"] == addr[0] and clients[uid]["port"] == addr[1]:
                        continue
                    try:
                        s.sendto(msg.getMsg(), (clients[uid]["ip"], clients[uid]["port"]))
                    except Exception as e:
                        logging.error("send to {}:{},err:{}".format(clients[uid]["ip"], clients[uid]["port"], e))

            # 200 占用通道请求
            if msg.msgType == 200:
                body = json.loads(msg.getBody())
                if body["channel_id"] in self.channels:
                    if "cur_user" not in self.channels[body["channel_id"]] or \
                            self.channels[body["channel_id"]]["cur_user"] is None or \
                            self.channels[body["channel_id"]]["cur_user"] == body["uid"]:

                        # 占用成功
                        self.channels[body["channel_id"]]["cur_user"] = body["uid"]
                        ret_msg = my_udp.udpMsg(msgType=200,
                                                body=json.dumps({"ret": True, "channel_id": body["channel_id"]}))
                        s.sendto(ret_msg.getMsg(), addr)
                    else:
                        # 当前channel已被占用，返回失败
                        ret_msg = my_udp.udpMsg(msgType=200, body=json.dumps(
                            {"ret": False, "cur_uid": self.channels[body["channel_id"]]["cur_user"]}),
                                                voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                else:
                    logging.error("invalid channel_id: {}".format(body["channel_id"]))

            # 201 释放通道请求
            elif msg.msgType == 201:
                body = json.loads(msg.getBody())
                if body["channel_id"] in self.channels:
                    logging.error(self.channels[body["channel_id"]])
                    if "cur_user" in self.channels[body["channel_id"]] and \
                            self.channels[body["channel_id"]]["cur_user"] == body["uid"]:

                        # 释放成功
                        self.channels[body["channel_id"]]["cur_user"] = None
                        ret_msg = my_udp.udpMsg(msgType=201, body=json.dumps({"ret": True}),
                                                voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                    else:
                        logging.warning(
                            "释放通道失败 用户ID或者通道ID错误: uid:{} channel_id:{}".format(body["uid"], body["channel_id"]))
                        # 当前用户已不再占用当前通道
                        ret_msg = my_udp.udpMsg(msgType=200, body=json.dumps({"ret": True}),
                                                voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                else:
                    logging.error("invalid channel_id: {}".format(body["channel_id"]))


# start
ChatServer()
