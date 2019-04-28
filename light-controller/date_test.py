import datetime

def time_to_ntp(date):
    ntp_const = datetime.datetime(1900, 1, 1, 0, 0, 0)

    diff = date - ntp_const
    timestamp = diff.days * 24 * 60 * 60 + diff.seconds
    return timestamp


if __name__ == "__main__":
    # 2006  # year
    # 11  # month
    # 21  # day
    # 16  # hour
    # 30  # minute
    # 0  # second
    # 1  # weekday (0 = Monday)
    # 325  # number of days since 1st January
    # -1  # dst - method tzinfo.dst() returned None

    _now = datetime.datetime.now()
    _to = datetime.datetime(2019, 4, 28, 13, 50)

    print(time_to_ntp(_now))
    print(time_to_ntp(_to))
