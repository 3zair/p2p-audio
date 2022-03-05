# from __future__ import print_function
# from ctypes import POINTER, cast
# import comtypes
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, EDataFlow, \
#     ERole
#
#
# # 封装一个class，调用方法
# class MyAudioUtilities(AudioUtilities):
#     @staticmethod
#     def GetDevice(id=None, default=0):
#         device_enumerator = comtypes.CoCreateInstance(
#             CLSID_MMDeviceEnumerator,
#             IMMDeviceEnumerator,
#             comtypes.CLSCTX_INPROC_SERVER)
#         if id is not None:
#             thisDevice = device_enumerator.GetDevice(id)
#         else:
#             if default == 0:
#                 # output
#                 thisDevice = device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
#             else:
#                 # input
#                 thisDevice = device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eCapture.value,
#                                                                        ERole.eMultimedia.value)
#         return thisDevice
#
#
# def main():
#     mixer_output = None
#     tmp = None
#     devicelist = MyAudioUtilities.GetAllDevices()
#     i = 0
#     for device in devicelist:
#         print(i, device)
#         i += 1
#     print(i, "Default Output")
#     i += 1
#     print(i, "Default Input")
#     i += 1
#     deviceSel = i
#
#     while (deviceSel >= i) or (deviceSel < 0):
#         print()
#         search = input("Which device 0 to " + str(i - 1) + ": ")
#         deviceSel = int(search)
#
#     if deviceSel < i - 2:
#         mixer_output = devicelist[int(search)]
#         print(mixer_output)
#         tmp = mixer_output.id
#         devices = MyAudioUtilities.GetDevice(tmp)
#     else:
#         if deviceSel == i - 2:
#             print("Default Output")
#             devices = MyAudioUtilities.GetDevice(tmp, 0)  # default output
#         else:
#             print("Default Input")
#             devices = MyAudioUtilities.GetDevice(tmp, 1)  # default input
#     print()
#     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#     volume = cast(interface, POINTER(IAudioEndpointVolume))
#
#     print("GetMute(): ", volume.GetMute())  # set using volume.SetMute(1, None)
#     print("GetMasterVolumeLevelScalar(): %s" % int(0.5 + 100.0 * volume.GetMasterVolumeLevelScalar()))
#     print("GetVolumeRange(): (%s, %s, %s)" % volume.GetVolumeRange())
#
#     newLevel = input("Enter new level (Ctrl C to quit): ")
#
#     intnewLevel = int(newLevel.replace('%', ''))
#     if intnewLevel < 0:  intnewLevel = 0.0
#     if intnewLevel > 100: intnewLevel = 100.0
#     print("SetMasterVolumeLevelScalar", intnewLevel / 100.0)
#     volume.SetMasterVolumeLevelScalar(intnewLevel / 100.0, None)
#     print("GetMasterVolumeLevelScalar(): %s" % int(0.5 + 100.0 * volume.GetMasterVolumeLevelScalar()))
#
#
# if __name__ == "__main__":
#     try:
#         while True:
#             main()
#             print()
#     except KeyboardInterrupt:
#         print()
