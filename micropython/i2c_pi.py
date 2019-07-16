import time
from datetime import datetime, timedelta


forced_state_light = 0

time_list_light = [datetime(2019, 1, 1, 12, 0), 12]

complete_list_light = [
    [datetime(2019, 1, 28, 14, 22), datetime(2019, 1, 27, 14, 22), 4,
     datetime(2019, 4, 28, 14, 22), 12],

    [datetime(2019, 4, 28, 14, 22), datetime(2019, 4, 27, 14, 22), 2,
     datetime(2019, 4, 28, 14, 22), 14],

    [datetime(2019, 5, 1, 2, 0), datetime(2019, 5, 29, 2, 0), 1,
     datetime(2019, 1, 1, 19, 00), 5]
]


def resp_force_light(state):
    force_state = {
        "force": state
    }
    return force_state


def resp_single_light(times):
    time, hours = times
    single_lifecycle = {
        "0": {
            "times": {
                "from": time,
                "hours": hours
            }
        }
    }
    return single_lifecycle


def resp_complete_light(datetimes):
    ret_dict = {}
    for i, _datetime in enumerate(datetimes):
        date_a, date_b, days, time, hours = _datetime
        ret_dict[str(i)] = {
            "from": date_a,
            "to": date_b,
            "days": days,
            "times": {
                "from": time,
                "hours": hours
            }
        }
    return ret_dict

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def process_single_light(_dict):

    time, hours = _dict["0"]["times"]["from"] , _dict["0"]["times"]["hours"]
    time_plus_hours = time + timedelta(hours=int(hours))

    print(is_time_between(time.time(), time_plus_hours.time()))





def process(_dict):
    _k = _dict.keys()

    if "force" in _k:
        pass
    else:
        if len(_k) > 1:
            pass
        else:
            process_single_light(_dict)

if __name__ == "__main__":
    while True:
        process(resp_single_light(time_list_light))
        time.sleep(1)
        