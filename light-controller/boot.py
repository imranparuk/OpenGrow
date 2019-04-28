import main
from ota import OTA

ota_url = 'http://192.168.8.130:5000/download/'
filename = 'main.py'

o = OTA(ota_url, filename)
o.update_file()

main.main()
