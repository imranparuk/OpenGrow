import utime
import ujson as json

import machine

from rtc import Rtc
from db import Db

LED_PIN = 2


class TempHumidController(object):
    def __init__(self, url, db_name='temphumidcontroller'):
        self.url = url
        self.led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)

        self.db = Db(url, db_name)
        self.data = None
        self.ppm = None

        # self.gpio_pins = {
        #     "ppm_sensor": 4,
        #     "co2_solenoid": 6,
        # }
        #
        # self.pins = {}
        # for key, val in self.gpio_pins.items():
        #     self.pins[key] = machine.Pin(val, machine.Pin.OUT)

        self.rtc = Rtc()
        self.url = url

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
        if b'ppm' in self.data.keys():
            self.ppm = self.data[b'ppm']

    def controller(self):
        pass



def main():
    url = 'http://192.168.8.130:5000/'

    lc = TempHumidController(url)
    lc()

    # while True:
    #     lc()
    #     utime.sleep(1)

main()

