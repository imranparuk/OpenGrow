import utime
import ujson as json

import machine

from rtc import Rtc
from db import Db

LED_PIN = 2


class Dispensor(object):
    def __init__(self, url, db_name='dispensor'):
        self.url = url
        self.led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)

        self.db = Db(url, db_name)
        self.data = None

        self.rtc = Rtc()
        self.url = url

        self.keys_to_pins = {
            "nutes": {
                "nutesA": 2,
                "nutesB": 4,
                "nutesC": 5,
            },
            "inOut": {
                "waterIn": 12,
                "out": 14
            },
            "waterLevel": 16,
            "mixer": None,
        }


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


    def process_data_db(self):
        if b'force' in self.data.keys():
            state = self.data[b'force']
            pass

        elif b'0' in self.data.keys():
            _cycle = b'0' if 'to' not in self.data[b'0'] else self.rtc.get_current_cycle(self.data)
            state = False
            if _cycle is not None:
                state = self.process_cycle_times(self.data, _cycle)

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
        water_in = data['inOut']['waterIn']


        _water_in_pin = machine.Pin(self.keys_to_pins['inOut']['waterIn'], machine.Pin.IN)
        _water_in_pin = machine.Pin(self.keys_to_pins['inOut']['waterIn'], machine.Pin.OUT)

        for key, dispense_val in nutes.items():
            _temp = machine.Pin(self.keys_to_pins['nutes'][key], machine.Pin.OUT)
            self.dispense_on_pin(_temp, dispense_val)




    def dispense_on_pin(self, pin, ml):
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

