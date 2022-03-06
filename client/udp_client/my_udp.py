import struct
import time

"""
100（音频传输的信号, 通道）:
`100 + t + body.len + body{"from":xx, "channel":"xx"} + data`

101（音频传输的信号, 私聊）:
`101 + t + body.len + body{"from":xx} + data`

200（占用某通道的请求）：
`200 + t +body.len + body{channel:1, uid:1}`
"""

HeaderSize = 12


class UdpMsg:
    def __init__(self, msgType=None, num=0, body="", voiceDataLen=700, voiceData="", msg=None):
        if msg is None:
            if msgType not in [100, 101, 200,201]:
                raise [Exception, "invalid msg type :{}".format(msgType)]
            self.body = body
            self.voiceData = voiceData
            self.msgNum = num
            self.msgType = msgType
            self.headers = [self.msgType, self.msgNum, len(body)]
            self.msg = struct.pack("!III", *self.headers) + self.body.encode()
            if msgType in [100, 101]:
                self.msg += voiceData
        else:
            if len(msg) > HeaderSize:
                self.msg = msg
                self.voiceData = ""
                self.headers = struct.unpack("!III", msg[:HeaderSize])
                self.msgType = self.headers[0]
                self.msgNum = self.headers[1]
                self.body = msg[HeaderSize:HeaderSize + self.headers[2]].decode()
                if self.msgType in [100, 101]:
                    self.voiceData = msg[HeaderSize + self.headers[2]:
                                         HeaderSize + self.headers[2] + voiceDataLen]
            else:
                raise [Exception, "invalid msg, len:{} is too short ".format(len(msg))]

    def getVoiceData(self):
        return self.voiceData

    def getMsg(self):
        return self.msg

    def getMsgNum(self):
        return self.msgNum

    def getMsgType(self):
        return self.msgType

    def getBody(self):
        return self.body
