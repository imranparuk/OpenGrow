import utime
import ujson as json
import urequests as requests
import machine

from rtc import Rtc
from db import Db

from utils import get_device_id_list

LED_PIN = 2


class Dispensor(object):
    def __init__(self, url, db_name='dispensor'):
        self.url = url
        self.led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)
        self.device = get_device_id_list()

        self.db = Db(url, db_name)
        self.data = None

        self.rtc = Rtc()

        self._keys_to_pins = self.get_keys_to_pins(self.url)
        self.pins = self.keys_to_pins(self._keys_to_pins)

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

    def get_keys_to_pins(self, url):
        json_payload = {
            "deviceId": self.device,
            "$OPTION": ["$GET_KEYS_TO_PINS"]
        }
        try:
            response = requests.post(url, json=json_payload)
            data = response.json()
            resp = data['pins']
            response.close()
            return resp
        except OSError:
            print("OS")
            return None

    def keys_to_pins(self, k_2_p):
        ret = {}
        for key, val in k_2_p.items():
            if type(val) == dict:
                _val = self.keys_to_pins(val)
            else:
                _val = machine.Pin(val if val > 0 else -val, machine.Pin.OUT if val > 0 else machine.Pin.IN)
            ret[key] = _val
        return ret

    def process_data_db(self):
        if b'force' in self.data.keys():
            state = self.data[b'force']
            pass

        elif b'0' in self.data.keys():
            _cycle = b'0' if 'to' not in self.data[b'0'] else self.rtc.get_current_cycle(self.data)
            if _cycle is not None:
                self.process_cycle_times(self.data, _cycle)

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
        _nutes = data['nutes']
        _in = data['in']
        _total_out = _in

        self.pins['mixer'].value(1)

        for key, dispense_val in _nutes.items():
            self.dispense_on_pin(self.pins['nutes'][key], dispense_val)
            _total_out += dispense_val

        while self.pins['sensor'].value() is not 1:
            self.dispense_on_pin(self.pins['in'], 10)
            # utime.sleep(0.001)

        #PH STUFF?

        self.dispense_on_pin(self.pins['out'], _total_out)
        self.pins['mixer'].value(1)

    def dispense_on_pin(self, pin, ml):
        pin.on()
        utime.sleep(ml*0.001)
        pin.off()


# from ota import OTA
def main():
    url = 'http://192.168.8.130:5000/'

    lc = Dispensor(url)
    lc()

    # while True:
    #     lc()
    #     utime.sleep(1)

main()

