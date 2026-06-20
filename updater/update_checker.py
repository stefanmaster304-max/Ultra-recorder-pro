import json
import requests
from utils.constants import APP_UPDATE_URL, APP_VERSION


def check_for_updates():
    try:
        response = requests.get(APP_UPDATE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        remote_version = data.get("version", "")
        current_parts = [int(x) for x in APP_VERSION.split(".")]
        remote_parts = [int(x) for x in remote_version.split(".")]
        if remote_parts > current_parts:
            return {
                "available": True,
                "version": remote_version,
                "download_url": data.get("download_url", ""),
                "checksum": data.get("checksum", ""),
                "changelog": data.get("changelog", []),
                "mandatory": data.get("mandatory", False),
            }
        return {"available": False, "version": APP_VERSION}
    except (requests.RequestException, json.JSONDecodeError, ValueError, KeyError):
        return None
