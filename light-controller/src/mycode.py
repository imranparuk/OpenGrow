import btree
import network
import machine
import time
import utime
import ujson as json
import urequests as requests
import ustruct as struct
import usocket as socket


class Db(object):
    def __init__(self, dbname='light_controller'):
        try:
            f = open(dbname, "r+b")
        except OSError:
            f = open(dbname, "w+b")
        self.db = btree.open(f)

        self.f = f

    def save(self, data):
        for key in data.keys():
            self.db[key] = json.dumps(data[key])
        self.db.flush()

    def load(self):
        ret_dict = {}
        for key in self.db.keys():
            ret_dict[key] = json.loads(self.db[key])
        return ret_dict

    def __del__(self):
        self.f.close()
        self.db.close()

class Rtc(object):
    def __init__(self):
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        self.NTP_DELTA = 3155673600

        self.host = "pool.ntp.org"
        self.rtc = machine.RTC()

    def get_datetime(self):
        return self.rtc.datetime()

    def get_NTP_time(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
        addr = socket.getaddrinfo(self.host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
        s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        return val - self.NTP_DELTA

    @staticmethod
    def set_time():
        t = time()
        tm = utime.localtime(t)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)

class LightController(object):
    def __init__(self, url, _pin):
        self.url = url
        self.do_connect_network()
        self.pin = machine.Pin(_pin, machine.Pin.OUT)
        self.db = Db(dbname="light_controller")

        self.cycle_num = 0

    def __call__(self, *args, **kwargs):
        pass

    def process_data_get(self):
        data = self.get_data(self.url)
        if data is not None:
            if 'force' in data.keys():
                if 'times' in data['force']:
                    pass
                else:
                    state = data['force']
                    res = self.set_relay(state)
                    print("Relay State: {}".format(res))
            elif '0' in data.keys():
                pass
            self.db.save(data)

    def get_current_cycle(self):
        data_dict = self.db.load()

        for i, val in data_dict.items():
            pass


    def set_relay(self, _int):
        if _int == 1:
            self.pin.high()
            print("high")
        elif _int == 0:
            self.pin.low()
            print("low")

    @staticmethod
    def do_connect_network():
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('HUAWEI-B618-D500', 'J7M12T3RMNR')  # connect to an AP
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())

    @staticmethod
    def get_data(_url):
        try:
            r = requests.get(_url)
            json_ret = r.json()
            r.close()
            return json_ret
        except OSError:
            print("OSError in request")
            return None

def main():

    # url = 'http://192.168.8.130:5000/'
    # lc = LightController(url, 2)
    # lc.process_data_get()
    # # while True:
    # #     lc.process_data_get()
    # #     time.sleep(1)

    db = Db('light_controller')
    print(db.load())

main()


