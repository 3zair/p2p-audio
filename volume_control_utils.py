# from ctypes import POINTER, cast
# import comtypes
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, EDataFlow, \
#     ERole
#
#
# # 封装的类用于实现制定device的id调节音量
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