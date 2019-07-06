from flask import Flask, jsonify, send_from_directory, send_file, request
import datetime

app = Flask(__name__)

forced_state_disp = [15, 20, 10, 2000]
time_list_disp = [datetime.datetime(2019, 4, 28, 14, 22), forced_state_disp]
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
    time, hours = times
    single_lifecycle = {
        "0": {
            "times": {
                "from": time_to_ntp(time),
                "hours": hours
            }
        }
    }
    return single_lifecycle


def resp_complete_light(datetimes):
    ret_dict = {}
    for i, _datetime in enumerate(datetimes):
        date_a, date_b, time, hours = _datetime
        ret_dict[str(i)] = {
            "from": time_to_ntp(date_a),
            "to": time_to_ntp(date_b),
            "times": {
                "from": time_to_ntp(time),
                "hours": hours
            }
        }
    return ret_dict


@app.route("/")
def home():
    # ret = resp_force_light(0)
    # ret = resp_force_time(time_list)
    ret = resp_complete_light(complete_list_light)

    return jsonify(ret)

@app.route("/version/", methods=['GET', 'POST'])
def version():
    print(request.get_json())
    ret = {
        "version": "0.0.0"
    }
    return jsonify(ret)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file('/home/imran/Documents/personal/projects/OpenGrow/server/OTA/{}'.format(filename), attachment_filename=filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
