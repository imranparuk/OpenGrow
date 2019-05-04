import btree
import network
import machine
import utime
import uos as os
import ujson as json
import urequests as requests
import ustruct as struct
import usocket as socket

from rtc import Rtc

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
            _cycle = b'0' if 'to' not in data[b'0'] else self.get_current_cycle(data)
            state = False
            if _cycle is not None:
                state = self.process_cycle(data, _cycle)
            res = self.set_relay(state)
            print("Relay State: {}".format(res))

    def process_cycle(self, data, cycle):
        _data = data[cycle]['times']
        _from = self.rtc.get_datetime_normilized_time(
            self.rtc.ntp_time_to_local(_data['from'])
        )
        _now = self.rtc.get_datetime_normilized_time(
            self.rtc.get_datetime()
        )
        hours = _data['hours']
        to_hours = _from[0]+hours
        to_hours = to_hours if not to_hours > 24 else to_hours - 24
        _to = (to_hours, _from[1], _from[2], 0)

        print(self.compare_times(self.rtc.get_time_int(_from), self.rtc.get_time_int(_now)))
        print(self.compare_times(self.rtc.get_time_int(_now), self.rtc.get_time_int(_to)))

        if self.compare_times(self.rtc.get_time_int(_from), self.rtc.get_time_int(_now)) and \
           self.compare_times(self.rtc.get_time_int(_now), self.rtc.get_time_int(_to)):
            return b'1'

        # print(_from)
        # print(_now)
        # print(_to)
        # print(self.rtc.get_time_int(_from))
        # print(self.rtc.get_time_int(_now))
        # print(self.rtc.get_time_int(_to))

        return b'0'

    def compare_times(self, timea, timeb):
        _t_const = self.rtc.get_time_int([12, 0, 0])

        if timea > _t_const > timeb:
            return True
        else:
            if timea < timeb:
                return True
        return False

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
            _from_int = self.rtc.get_date_int(_from)
            _to_int = self.rtc.get_date_int(_to)
            _now_int = self.rtc.get_date_int(_now)

            if _from_int < _now_int < _to_int:
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

    # ota_url = 'http://192.168.8.130:5000/download/'
    # v_url = 'http://192.168.8.130:5000/version/'
    # o = OTA(ota_url, v_url)

    url = 'http://192.168.8.130:5000/'
    lc = LightController(url, 2)
    lc()
    #
    # while True:
    #     lc()
    #     utime.sleep(1)

main()

