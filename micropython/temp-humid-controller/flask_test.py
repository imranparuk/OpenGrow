from flask import Flask, jsonify, send_from_directory, send_file, request
import datetime

app = Flask(__name__)

temp_humid = [
    [24, 4],
    [50, 5]
]


def resp_get_temp_humid(_temp_humid):
    temp, temp_h, humid, humid_h = temp_humid


    return  {
        "temp": temp,
        "temp_h": temp_h,

    }


@app.route("/")
def home():
    ret = resp_get_temp_humid(ppm_level)

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
