from utils import do_connect_network

url = 'http://192.168.8.161:5000/'
type = "light_controller"

do_connect_network()

# from ota import OTA
# o = OTA(url, type)

import main
