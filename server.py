import socket
import my_udp
import json

TEST_CLIENT_IP = socket.gethostbyname(socket.gethostname())


def getClients():
    return [("192.168.110.189", 8001), ("192.168.110.123", 8002)]


class ChatServer:
    def __init__(self, id, ip, port):
        # 建立IPv4,UDP的socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口：
        s.bind((ip, port))
        # 不需要开启listen，直接接收所有的数据
        print('Bind UDP on {}'.format(port))

        clients = getClients()
        while True:
            # 接收来自客户端的数据,使用recvfrom
            data, addr = s.recvfrom(1024)
            print('Received from {}'.format(addr))
            for c in clients:
                # broadcast
                if c == addr:
                    continue
                msg = my_udp.udpMsg(body=json.dumps({"from": addr, "channel": id}), voiceDataLen=1024,
                                    voiceData=data)
                s.sendto(msg.getMsg(), c)
