if __name__ == '__main__':
    device_list = conf.get_device_conf()
    devices = {
        "inputs": [],
        "phone_input": [],
        "pc_outputs": [],
        "usb_outputs": [],
        "phone_output": []
    }

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        max_input_channels = p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')
        max_output_channels = p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')
        name = p.get_device_info_by_host_api_device_index(0, i).get('name')
        if not name.endswith(")"):
            name += ")"
        if max_input_channels > 0:
            print("input device id ", i, "-", name)
            if name in device_list['phone_input']:
                devices["phone_input"].append(i)
            elif name in device_list['headset_input']:
                devices["inputs"].append(i)
        if max_output_channels > 0:
            print("output device id ", i, "-", name)
            if name in device_list['phone_output']:
                devices["phone_output"].append(i)
            elif name in device_list['headset_output']:
                devices["usb_outputs"].append(i)
            elif name in device_list['default_output']:
                devices["pc_outputs"].append(i)
    return devices
