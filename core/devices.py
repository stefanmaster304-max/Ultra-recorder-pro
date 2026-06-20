import sounddevice as sd


def get_input_devices():
    devices = sd.query_devices()
    return [d for d in devices if d["max_input_channels"] > 0]


def get_output_devices():
    devices = sd.query_devices()
    return [d for d in devices if d["max_output_channels"] > 0]


def get_device_name(device_id):
    try:
        dev = sd.query_devices(device_id)
        return dev["name"]
    except (ValueError, IndexError):
        return "Unknown"


def get_default_input_device():
    try:
        return sd.default.device[0]
    except Exception:
        devices = get_input_devices()
        return devices[0]["index"] if devices else None


def get_default_output_device():
    try:
        return sd.default.device[1]
    except Exception:
        devices = get_output_devices()
        return devices[0]["index"] if devices else None


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
