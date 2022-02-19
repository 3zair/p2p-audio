import serial
import time

portx = "/dev/tty.usbserial-1130"
bps = 9600
timex = 15
ser = serial.Serial(None, bps, rtscts=True, dsrdtr=True)


def rec_tra():
    ser.setPort(portx)
    # ser.dsrdtr = True
    # ser.rtscts = True
    ser.dtr = False
    ser.open()
    while True:
        for i in range(0, 100):
            i += 1
            print(i, " DTR:", ser.dtr, "CD: ", ser.cd, " DSR:", ser.dsr, " CTS:", ser.cts)
            time.sleep(0.022)


if __name__ == '__main__':
    try:
        rec_tra()
    except KeyboardInterrupt:
        if ser is not None:
            ser.close()