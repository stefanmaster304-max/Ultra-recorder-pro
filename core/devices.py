import sounddevice as sd


def get_input_devices():
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    return [d for d in devices if _is_input_device(d)]


def get_output_devices():
    devices = sd.query_devices()
    return [d for d in devices if _is_output_device(d)]


def _is_input_device(device):
    if device["max_input_channels"] <= 0:
        return False
    if device["max_output_channels"] >= device["max_input_channels"] and device["max_output_channels"] > 0:
        return False
    name = device["name"].lower()
    output_keywords = ["speaker", "alto-falante", "altavoz", "headphone", "fone", "headset", "output"]
    for kw in output_keywords:
        if kw in name:
            input_keywords = ["microphone", "mic", "mix", "stereo", "est\u00e9reo", "input"]
            if not any(ik in name for ik in input_keywords):
                return False
    return True


def _is_output_device(device):
    if device["max_output_channels"] <= 0:
        return False
    if device["max_input_channels"] >= device["max_output_channels"] and device["max_input_channels"] > 0:
        return False
    name = device["name"].lower()
    input_keywords = ["microphone", "mic", "input"]
    for kw in input_keywords:
        if kw in name:
            return False
    return True


def get_device_name(device_id):
    try:
        dev = sd.query_devices(device_id)
        return dev["name"]
    except (ValueError, IndexError):
        return "Unknown"


def get_default_input_device():
    try:
        devices = get_input_devices()
        if devices:
            return devices[0]["index"]
        return sd.default.device[0]
    except Exception:
        return None


def get_default_output_device():
    try:
        devices = get_output_devices()
        if devices:
            return devices[0]["index"]
        return sd.default.device[1]
    except Exception:
        return None


def get_device_sample_rates(device_id):
    try:
        dev = sd.query_devices(device_id)
        rates = []
        for rate in [44100, 48000, 96000, 192000]:
            try:
                sd.check_input_settings(device=device_id, samplerate=rate)
                rates.append(rate)
            except Exception:
                try:
                    sd.check_output_settings(device=device_id, samplerate=rate)
                    rates.append(rate)
                except Exception:
                    pass
        return rates if rates else [48000]
    except Exception:
        return [48000]
