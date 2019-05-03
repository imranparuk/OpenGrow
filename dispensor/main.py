import btree
import network
import machine
import utime
import uos as os
import ujson as json
import urequests as requests
import ustruct as struct
import usocket as socket

def do_connect_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('HUAWEI-B618-D500', 'J7M12T3RMNR')  # connect to an AP
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

do_connect_network()

LED_PIN = 2

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


class Rtc(object):
    def __init__(self):
        #todo: sync times in a local manner

        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        self.NTP_DELTA = 3155673600
        self.host = "time.nmisa.org" #"pool.ntp.org"
        self.rtc = machine.RTC()

    def get_datetime(self):
        #  (year, month, day, weekday, hours, minutes, seconds, subseconds)
        return self.rtc.datetime()

    @staticmethod
    def get_datetime_normilized_time(datetime):
        #(year, month, day, weekday, hours, minutes, seconds, subseconds)
        return (0, 0, 0, 0, datetime[4], datetime[5], datetime[6], datetime[7])

    @staticmethod
    def get_datetime_normilized_date(datetime):
        #(year, month, day, weekday, hours, minutes, seconds, subseconds)
        return (datetime[0], datetime[1], datetime[2], datetime[3], 0, 0, 0, 0)

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

    def ntp_time_to_local(self, t):
        tm = utime.localtime(t)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        return tm

    def set_time_network(self):
        t = self.get_NTP_time()
        tm = self.ntp_time_to_local(t)
        machine.RTC().datetime(tm)


class Dispensor(object):
    def __init__(self, url, db_name='dispensor'):
        self.url = url
        self.led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)

        self.f = self.db_init(db_name)
        self.db = btree.open(self.f)
        self.db_delete()

        self.rtc = Rtc()

        self.key_to_pin = {
            "nutesA": 2,
            "nutesB": 4,
            "nutesC": 5,
            "water": 12,
            "out": 14,
            "waterLevel": 16
        }

    def __call__(self, *args, **kwargs):
        self.rtc.set_time_network()
        pdg = self.process_data_get()
        print("Saved Db: {}".format(pdg))
        if pdg:
            self.process_data_db()
        else:
            print("No Data")

    def __del__(self):
        self.f.close()
        self.db.close()

    def db_print(self):
        for key in self.db.keys():
            print(key)

    def db_delete(self):
        for key in self.db.keys():
            del self.db[key]

    def db_save(self, data):
        for key in data.keys():
            self.db[key] = json.dumps(data[key])
        self.db.flush()

    def db_load(self):
        ret_dict = {}
        for key in self.db.keys():
            ret_dict[key] = json.loads(self.db[key])
        return ret_dict

    @staticmethod
    def db_init(dbname):
        try:
            f = open(dbname, "r+b")
            print("db opened")
        except OSError:
            f = open(dbname, "w+b")
            print("db created")
        return f

    def process_data_get(self):
        data = get_data(self.url)
        if data is not None:
            self.db_save(data)
            return True
        return False

    def process_data_db(self):
        if 'force' in self.db.keys():
            # state = self.db.get('force')
            # print("state: {}".format(state))
            # res = self.set_relay(state)
            # print("Relay State: {}".format(res))
            pass
        elif b'0' in self.db.keys():
            self.process_cycle()

    def process_cycle(self):
        data = self.db_load()
        _cycle = b'0' if 'dates' not in data[b'0'] else self.get_current_cycle(data)
        if _cycle is not None:
            self.process_cycle_times(data, _cycle)

    def process_cycle_times(self, data, cycle):
        _time = data[cycle]['time']
        _data = data[cycle]['dispense']

        _t = self.rtc.get_datetime_normilized_time(
            self.rtc.ntp_time_to_local(_time)
        )
        _now = self.rtc.get_datetime_normilized_time(
            self.rtc.get_datetime()
        )

        dispensed = self.get_dispensed_today(_now)
        if not dispensed:
            if _now > _t:
                self.dispense(_data)
                self.set_dispensed_today()

    def get_current_cycle(self, data):
        _now = self.rtc.get_datetime_normilized_date(self.rtc.get_datetime())
        _cycle = None
        for key in sorted(data.keys()):
            i, val = key, data[key]
            _from = self.rtc.get_datetime_normilized_date(
                self.rtc.ntp_time_to_local(val['dates']['from'])
            )
            _to = self.rtc.get_datetime_normilized_date(
                self.rtc.ntp_time_to_local(val['dates']['to'])
            )
            _days = val['dates']['days']
            if _from < _now < _to:
                if self.process_cycle_dates(_from, _now, _days):
                    _cycle = i
        return _cycle

    def process_cycle_dates(self, _from, _now, _days):
        _from_day = _from[2]
        _now_day = _from[2]
        _diff = _now_day - _from_day
        if _diff == 0:
            return True
        if _diff % _days:
            return True
        return False

    def get_dispensed_today(self, date):
        if b'date' not in self.db.keys():
            return False
        current_day = json.loads(self.db[b'date'])
        if date == current_day:
            return True
        return False

    def set_dispensed_today(self):
        _now = self.rtc.get_datetime_normilized_date(self.rtc.get_datetime())
        self.db[b'date'] = json.dumps(_now)
        self.db.flush()

    def dispense(self, data):
        nutes = data['nutes']
        water = data['water']

        for key, dispense_val in nutes.items():
            _temp = machine.Pin(self.key_to_pin[key], machine.Pin.OUT)
            self.dispense_pin(_temp, dispense_val)



    def dispense_pin(self, pin, ml):
        pin.on()
        utime.sleep(ml*0.001)
        pin.off()


# from ota import OTA
def main():
    url = 'http://192.168.8.130:5000/'
    # ota_url = 'http://192.168.8.130:5000/download/'
    # v_url = 'http://192.168.8.130:5000/version/'
    #
    # o = OTA(ota_url, v_url)

    lc = Dispensor(url)
    lc()

    # while True:
    #     lc()
    #     utime.sleep(1)

main()

