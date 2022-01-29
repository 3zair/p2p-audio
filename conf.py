import pyaudio
# EXCHANGE msg type
CLIENT_ADD = "add"  # add client
CLIENT_DEL = "del"  # del client
CLIENT_UPDATE_ALL = "update_all"

# TCP MSG type
MSG_HEALTHY = 0  # 心跳包
MSG_EXCHANGE = 1
MSG_Voice = 2

HEADER_SIZE = 8

AUDIO_BYTE_SIZE = 1024

# pyaudio onf
chunk_size = 1024  # 512
audio_format = pyaudio.paInt16
channels = 1
rate = 20000
