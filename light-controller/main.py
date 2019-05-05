import machine

from rtc import Rtc
from db import Db


class LightController(object):
    def __init__(self, url, _pin, db_name='light_c'):
        self.url = url
        self.pin = machine.Pin(_pin, machine.Pin.OUT)

        self.db = Db(url, db_name)
        self.data = None

        self.rtc = Rtc()

    def __call__(self, *args, **kwargs):
        self.rtc.set_time_network()
        pdg = self.db()
        print("Saved Db: {}".format(pdg))
        if pdg:
            self.data = self.db.db_load()
            if self.data is not None:
                self.process_data_db()
            else:
                print("No Data")
        else:
            print("No Data, default to off mode")
            self.set_relay(b'0')

    def process_data_db(self):
        if b'force' in self.data.keys():
            state = self.data[b'force']
            print("state: {}".format(state))
            res = self.set_relay(state)
            print("Relay State: {}".format(res))
        elif b'0' in self.data.keys():
            _cycle = b'0' if 'to' not in self.data[b'0'] else self.rtc.get_current_cycle(self.data)
            state = False
            if _cycle is not None:
                state = self.process_cycle_times(self.data, _cycle)
            res = self.set_relay(state)
            print("Relay State: {}".format(res))

    def process_cycle_times(self, data, cycle):

        _data = data[cycle]['times']
        _from = self.rtc.get_datetime_normilized_time(
            self.rtc.ntp_time_to_local(_data['from'])
        )
        _now = self.rtc.get_datetime_normilized_time(
            self.rtc.get_datetime()
        )
        hours = _data['hours']
        to_hours = _from[1]+hours
        to_days = 0

        if to_hours > 24:
            to_days = 1
            to_hours = to_hours - 24

        _to = (to_days, to_hours, _from[2], _from[3], 0)

        # print(_from)
        # print(_now)
        # print(_to)
        # print(self.rtc.get_time_int(_from))
        # print(self.rtc.get_time_int(_now))
        # print(self.rtc.get_time_int(_to))

        if _from < _now < _to:
            return b'1'
        return b'0'

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

