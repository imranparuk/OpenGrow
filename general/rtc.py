import machine
import urequests as requests
import ustruct as struct
import usocket as socket
import utime as time

class Rtc(object):
    def __init__(self):
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        self.NTP_DELTA = 3155673600
        self.host = "time.nmisa.org" #"pool.ntp.org"
        self._rtc = machine.RTC()

    def get_datetime(self):
        #  (year, month, day, weekday, hours, minutes, seconds, subseconds)
        return self._rtc.datetime()

    @staticmethod
    def get_datetime_normilized_time(datetime):
        #(year, month, day, weekday, hours, minutes, seconds, subseconds)
        return (datetime[4], datetime[5], datetime[6], datetime[7])

    @staticmethod
    def get_time_int(time):
        # hours, minutes, seconds, subseconds
        # excludes milliseconds
        return time[0]*60*60*24 + time[1]*60*60 + time[2]*60 + time[3]

    @staticmethod
    def get_date_int(date):
        # year, month, day
        # assumes there will only be 10k years, idk python wont be around by then, but i surely wont

        a = int((14 - date[1]) / 12)
        y = date[0] + 4800 - a
        m = date[1] + 12 * a - 3
        return date[2] + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045
        # return date[0]*10000 + date[1]*100 + date[2]

    @staticmethod
    def get_datetime_normilized_date(datetime):
        #(year, month, day, weekday, hours, minutes, seconds, subseconds)
        return (datetime[0], datetime[1], datetime[2])

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
        tm = time.localtime(t)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        return tm

    def set_time_network(self):
        t = self.get_NTP_time()
        tm = self.ntp_time_to_local(t)
        machine.RTC().datetime(tm)