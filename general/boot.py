from ota import OTA
from utils import do_connect_network

ota_url = 'http://192.168.8.130:5000/download/'
v_url = 'http://192.168.8.130:5000/version/'
type = "light_controller"

do_connect_network()
o = OTA(ota_url, v_url, type)

import main
