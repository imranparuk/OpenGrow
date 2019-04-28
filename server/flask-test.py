from flask import Flask, jsonify, send_from_directory, send_file
import datetime

app = Flask(__name__)

forced_state = 1
time_list = [datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 17, 22)]
complete_list = [
    [datetime.datetime(2019, 1, 28, 14, 22), datetime.datetime(2019, 1, 27, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 17, 22)],

    [datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 27, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 17, 22)],

    [datetime.datetime(2019, 4, 26, 14, 22), datetime.datetime(2019, 4, 29, 14, 22),
     datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 28, 22, 22)]
]


def time_to_ntp(date):
    ntp_const = datetime.datetime(2000, 1, 1, 2, 0)
    # ntp_const = datetime.datetime(2000, 1, 1, 0, 0, 0)
    diff = date - ntp_const
    timestamp = diff.days * 24 * 60 * 60 + diff.seconds
    return timestamp


def resp_force(state):
    force_state = {
        "force": state
    }
    return force_state


def resp_force_time(times):
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


def resp_complete(datetimes):
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


@app.route("/")
def home():
    ret = resp_force(0)
    # ret = resp_force_time(time_list)
    # ret = resp_complete(complete_list)

    return jsonify(ret)

@app.route("/version/")
def version():
    ret = {
        "version": "0.1.0"
    }
    return jsonify(ret)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file('/home/imran/Documents/personal/projects/OpenGrow/server/OTA/{}'.format(filename), attachment_filename=filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
