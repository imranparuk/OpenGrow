from flask import Flask, jsonify, send_from_directory, send_file, request
import datetime

app = Flask(__name__)

forced_state_light = 0
time_list_light = [datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 17, 22)]
complete_list_light = [
    [datetime.datetime(2019, 1, 28, 14, 22), datetime.datetime(2019, 1, 27, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 17, 22)],

    [datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 27, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 17, 22)],

    [datetime.datetime(2019, 4, 26, 14, 22), datetime.datetime(2019, 4, 29, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 22, 22)]
]

forced_state_disp = [15, 20, 10, 2000]
time_list_disp = [datetime.datetime(2019, 4, 28, 14, 22)]
complete_list_disp = [
    [datetime.datetime(2019, 1, 28, 14, 22), datetime.datetime(2019, 1, 27, 14, 22),
     datetime.datetime(2019, 4, 28, 17, 22),
     1],

    [datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 27, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22),
     1],

    [datetime.datetime(2019, 4, 26, 14, 22), datetime.datetime(2019, 4, 29, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22),
     3]
]


def time_to_ntp(date):
    ntp_const = datetime.datetime(2000, 1, 1, 2, 0)
    # ntp_const = datetime.datetime(2000, 1, 1, 0, 0, 0)
    diff = date - ntp_const
    timestamp = diff.days * 24 * 60 * 60 + diff.seconds
    return timestamp


def resp_force_light(state):
    force_state = {
        "force": state
    }
    return force_state


def resp_force_time_light(times):
    time_a, time_b = times
    single_lifecycle = {
        "0": {
            "times": {
                "from": time_to_ntp(time_a),
                "to": time_to_ntp(time_b)
            }
        }
    }
    return single_lifecycle


def resp_complete_light(datetimes):
    ret_dict = {}
    for i, _datetime in enumerate(datetimes):
        date_a, date_b, time_a, time_b = _datetime
        ret_dict[str(i)] = {
            "from": time_to_ntp(date_a),
            "to": time_to_ntp(date_b),
            "times": {
                "from": time_to_ntp(time_a),
                "to": time_to_ntp(time_b)
            }
        }
    return ret_dict

def resp_complete_disp(times, data):
    date_a, date_b, time, days = times
    nutes_a, nutes_b, nutes_c, water = data
    single_lifecycle = {
        "0": {
            "dispense": {
                "nutes": {
                    "nutesA": nutes_a,
                    "nutesB": nutes_b,
                    "nutesC": nutes_c,
                },
                "water": water
            },
            "dates": {
                "from": time_to_ntp(date_a),
                "to": time_to_ntp(date_b),
                "days": days
            },
            "time": time_to_ntp(time),
        }
    }
    return single_lifecycle

# def resp_complete_disp(datetimes):
#     ret_dict = {}
#     for i, _datetime in enumerate(datetimes):
#         date_a, date_b, time_a, time_b, days = _datetime
#         ret_dict[str(i)] = {
#             "from": time_to_ntp(date_a),
#             "to": time_to_ntp(date_b),
#             "days": days,
#             "times": {
#                 "from": time_to_ntp(time_a),
#                 "to": time_to_ntp(time_b)
#             }
#         }
#     return ret_dict


@app.route("/")
def home():
    ret = resp_force_light(0)
    # ret = resp_force_time(time_list)
    # ret = resp_complete(complete_list)

    # a =     [datetime.datetime(2019, 5, 1, 14, 22), datetime.datetime(2019, 5, 5, 14, 22),
    #  datetime.datetime(2019, 4, 28, 17, 22),
    #  1]
    # ret = resp_complete_disp(a, [15, 20, 10, 2000])
    return jsonify(ret)

@app.route("/version/", methods=['GET', 'POST'])
def version():
    print(request.get_json())
    ret = {
        "version": "0.1.0"
    }
    return jsonify(ret)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file('/home/imran/Documents/personal/projects/OpenGrow/server/OTA/{}'.format(filename), attachment_filename=filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
