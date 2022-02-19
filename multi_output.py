import threading
from threading import Thread
import pyaudio
import wave

chunk = 1024

# open a wav format music
f = wave.open("input.wav", "rb")
data = f.readframes(chunk)
# instantiate PyAudio
p = pyaudio.PyAudio()
# open stream
#
# # paly stream
# while data != '':
#     stream.write(data)
#     data = f.readframes(chunk)
#
# # stop stream
# stream.stop_stream()
# stream.close()
#
# # close PyAudio
# p.terminate()


def audioFunc1():
    global data
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=f.getframerate(),
                    frames_per_buffer=chunk,
                    output=True,
                    output_device_index=1)
    # read data
    while len(data) > 0:
        stream.write(data)
        data = f.readframes(chunk)


def audioFunc2():
    global data
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=f.getframerate(),
                    frames_per_buffer=chunk,
                    output=True,
                    output_device_index=2)
    # read data
    while len(data) > 0:
        stream.write(data)
        data = f.readframes(chunk)


if __name__ == '__main__':
    Thread(target=audioFunc1).start()
    Thread(target=audioFunc2).start()