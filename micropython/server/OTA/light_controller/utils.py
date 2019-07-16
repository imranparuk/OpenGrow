import ujson as json
import network
import machine
import urequests as requests

CONFIG_FILE = "/config.json"

def get_device_id_list():
    return [i for i in machine.unique_id()]

def do_connect_network():
    json = read_json_file(CONFIG_FILE)
    ssid, password = json['network']['ssid'], json['network']['password']
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)  # connect to an AP
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


def read_json_file(filename):
    try:
        with open(filename, 'r') as f:
            data = json.loads(f.read())
            return data
    except OSError:
        print("OSError in Json file, file may not exist")
        return None

def write_json_file(filename, data):
    try:
        with open(filename, 'w') as f:
            f.write(json.dumps(data))
            return True
    except OSError:
        print("OSError in Json file, file may not exist")
        return False

def get_data(_url):
    try:
        r = requests.get(_url)
        json_ret = r.json()
        r.close()
        return json_ret
    except OSError:
        print("OSError in request")
        return None
    except MemoryError:
        pass