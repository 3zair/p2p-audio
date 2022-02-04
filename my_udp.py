import struct


class udpMsg:
    def __init__(self, body=None, voiceDataLen=1024, voiceData=None, msg=None):
        if msg is None:
            self.body = body
            self.voiceData = voiceData
            self.headers = [len(body)]
            self.msg = struct.pack("!I", *self.headers) + self.body.encode() + voiceData
        else:
            if len(msg) > 4:
                self.headers = struct.unpack("!I", msg[:4])
                self.body = msg[4:4 + self.headers[0]].decode()
                self.msg = msg
                self.voiceData = msg[4 + self.headers[0]:4 + self.headers[0] + voiceDataLen]
            else:
                raise [Exception, "invalid msg, len:{} is too short ".format(len(msg))]

    def getVoiceData(self):
        return self.voiceData

    def getMsg(self):
        return self.msg

    def getBody(self):
        return self.body
