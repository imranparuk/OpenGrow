import btree
import network
import machine
import utime
import uos as os
import ujson as json
import urequests as requests
import ustruct as struct
import usocket as socket


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

class LightController(object):
    def __init__(self, url, _pin, db_name='light_c'):
        self.url = url
        self.pin = machine.Pin(_pin, machine.Pin.OUT)

        self.f = self.db_init(db_name)
        self.db = btree.open(self.f)
        self.db_delete()

        self.rtc = Rtc()

    def __call__(self, *args, **kwargs):
        self.rtc.set_time_network()
        pdg = self.process_data_get()
        print("Saved Db: {}".format(pdg))
        if pdg:
            self.process_data_db()
        else:
            print("No Data, default to off mode")
            self.set_relay(b'0')

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
            state = self.db.get('force')
            print("state: {}".format(state))
            res = self.set_relay(state)
            print("Relay State: {}".format(res))
        elif b'0' in self.db.keys():
            data = self.db_load()
            if 'to' not in data[b'0']:
                self.process_cycle(data, b'0')
            else:
                _cycle = self.get_current_cycle(data)
                state = False
                if _cycle is not None:
                    state = self.process_cycle(data, _cycle)

                res = self.set_relay(state)
                print("Relay State: {}".format(res))

    def process_cycle(self, data, cycle):
        _data = data[cycle]['times']
        _to = self.rtc.get_datetime_normilized_time(
            self.rtc.ntp_time_to_local(_data['to'])
        )
        _from = self.rtc.get_datetime_normilized_time(
            self.rtc.ntp_time_to_local(_data['from'])
        )
        _now = self.rtc.get_datetime_normilized_time(
            self.rtc.get_datetime()
        )
        if _from < _now < _to:
            return b'1'
        return b'0'

    def get_current_cycle(self, data):
        _now = self.rtc.get_datetime_normilized_date(self.rtc.get_datetime())
        _cycle = None
        for key in sorted(data.keys()):
            i, val = key, data[key]
            _from = self.rtc.get_datetime_normilized_date(
                self.rtc.ntp_time_to_local(val['from'])
            )
            _to = self.rtc.get_datetime_normilized_date(
                self.rtc.ntp_time_to_local(val['to'])
            )
            if _from < _now < _to:
                _cycle = i
        return _cycle

    def set_relay(self, _state):
        if _state is True or _state == b'1' or _state == 1:
            try:
                self.pin.on()
            except AttributeError:
                self.pin.high()
            print("high")
            return True

        elif _state is False or _state == b'0' or _state == 0:
            try:
                self.pin.off()
            except AttributeError:
                self.pin.low()
            print("low")
            return False

# from ota import OTA
def main():

    url = 'http://192.168.8.130:5000/'
    ota_url = 'http://192.168.8.130:5000/download/'
    v_url = 'http://192.168.8.130:5000/version/'
    #
    # o = OTA(ota_url, v_url)

    lc = LightController(url, 2)
    # lc()

    while True:
        lc()
        utime.sleep(1)

main()

