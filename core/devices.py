import sounddevice as sd


def get_input_devices():
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    return [d for d in devices if _is_input_device(d, hostapis)]


def get_output_devices():
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    return [d for d in devices if _is_output_device(d, hostapis)]


def _is_input_device(device, hostapis):
    if device["max_input_channels"] <= 0:
        return False
    if device["max_output_channels"] > 0 and device["max_input_channels"] <= device["max_output_channels"]:
        return False
    hostapi = hostapis[device["hostapi"]]
    name = device["name"].lower()
    if "output" in name or "speaker" in name or "alto-falante" in name or "altavoz" in name or "fone" in name:
        if "microphone" not in name and "mic" not in name:
            return False
    return True


def _is_output_device(device, hostapis):
    if device["max_output_channels"] <= 0:
        return False
    if device["max_input_channels"] > 0 and device["max_output_channels"] <= device["max_input_channels"]:
        return False
    hostapi = hostapis[device["hostapi"]]
    name = device["name"].lower()
    if "microphone" in name or "mic" in name or "input" in name:
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
