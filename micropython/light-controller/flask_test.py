from flask import Flask, jsonify, send_from_directory, send_file, request
import datetime

app = Flask(__name__)

forced_state_light = 0
time_list_light = [datetime.datetime(2019, 4, 25, 0, 0), 12]
complete_list_light = [
    [datetime.datetime(2019, 1, 28, 14, 22), datetime.datetime(2019, 1, 27, 14, 22), 4,
     datetime.datetime(2019, 4, 28, 14, 22), 12],

    [datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 27, 14, 22), 2,
     datetime.datetime(2019, 4, 28, 14, 22), 14],

    [datetime.datetime(2019, 5, 1, 2, 0), datetime.datetime(2019, 5, 29, 2, 0), 1,
     datetime.datetime(2019, 1, 1, 19, 00), 5]
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
        date_a, date_b, days, time, hours = _datetime
        ret_dict[str(i)] = {
            "from": time_to_ntp(date_a),
            "to": time_to_ntp(date_b),
            "days": days,
            "times": {
                "from": time_to_ntp(time),
                "hours": hours
            }
        }
    return ret_dict

@app.route("/", methods=['GET', 'POST'])
def home():
    req = request.get_json()
    resp = {}

    if "$OPTION" in req.keys():
        options = req["$OPTION"]
        if "$GET_VERSION" in options:
            resp['version'] = "0.0.0"
        if "$GET_FILES" in options:
            import os
            files_ = os.listdir('/home/imran/Documents/personal/projects/OpenGrow/server/OTA/light_controller')
            resp['files'] = files_
            print(files_)
            resp['filesUrl'] = 'http://192.168.8.130:5000'
            print("get files")

        if "$DOWNLOAD_FILE" in options:
            file = options['$DOWNLOAD_FILE']
            send_file('/home/imran/Documents/personal/projects/OpenGrow/server/OTA/{}'.format(file),
                      attachment_filename=file)
        if "$GET_DATA" in options:
            # ret = resp_force_light(1)
            ret = resp_force_time_light(time_list_light)
            # ret = resp_complete_light(complete_list_light)
            resp["data"] = ret
            print("herehere")

    return jsonify(resp)

# @app.route('/download/<path:filename>', methods=['GET', 'POST'])
# def download(filename):
#     return

# @app.route("/version/", methods=['GET', 'POST'])
# def version():
#     print(request.get_json())
#     ret = {
#         "version": "0.0.0"
#     }
#     return jsonify(ret)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
