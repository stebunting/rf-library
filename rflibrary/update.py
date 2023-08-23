import json
import requests
import data

def check():
    rtn = {
        "connection": False,
        "version": "",
        "path": ""
    }

    try:
        req = requests.get(data.UPDATE_FILE_LOCATION, timeout=3)
        rtn["connection"] = req.status_code == 200
    except requests.exceptions.ConnectionError:
        rtn["connection"] = False

    if rtn["connection"]:
        latest = json.loads(req.text)
        try:
            win = latest["win"]
            rtn["version"] = win["version"]
            rtn["path"] = win["path"]
        except KeyError:
            rtn["connection"] = False
    return rtn
