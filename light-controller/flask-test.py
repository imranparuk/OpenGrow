from flask import Flask, jsonify
import datetime

app = Flask(__name__)

complete_lightcycle = {
    0: {
        "from": "A",
        "to": "B",
        "times": {
            "from": "timeA",
            "to": "timeB"
        }
    },
    1: {
        "from": "A",
        "to": "B",
        "times": {
            "from": "timeA",
            "to": "timeB"
        }
    },
    2: {
        "from": "A",
        "to": "B",
        "times": {
            "from": "timeA",
            "to": "timeB"
        }
    },
    3: {
        "from": "A",
        "to": "B",
        "times": {
            "from": "timeA",
            "to": "timeB"
        }
    }
}

# single_lifecycle = {
#     "force": {
#         "times": {
#             "from": "timeA",
#             "to": "timeB"
#         }
#     }
# }

force_on_state = {
    "force": 1
}

force_off_state = {
    "force": 0
}

# date1 = datetime.datetime.utcnow()

def time_to_ntp(date):
    ntp_const = datetime.datetime(2000, 1, 1, 0, 0, 0)

    diff = date - ntp_const
    timestamp = diff.days * 24 * 60 * 60 + diff.seconds
    return timestamp

def time_to_resp(data):
    timea, timeb = data
    datea1, datea2 = datetime.datetime(2019, 1, 28, 14, 22), datetime.datetime(2019, 1, 27, 14, 22)
    dateb1, dateb2 = datetime.datetime(2019, 4, 28, 14, 22), datetime.datetime(2019, 4, 27, 14, 22)
    datec1, datec2 = datetime.datetime(2019, 4, 26, 14, 22), datetime.datetime(2019, 4, 27, 14, 22)


    single_lifecycle = {
        "0": {
            "from": time_to_ntp(datea1),
            "to": time_to_ntp(datea2),
            "times": {
                "from": time_to_ntp(timea),
                "to": time_to_ntp(timeb)
            }
        },
        "1": {
            "from": time_to_ntp(dateb1),
            "to": time_to_ntp(dateb2),
            "times": {
                "from": time_to_ntp(timea),
                "to": time_to_ntp(timeb)
            }
        },
        "2": {
            "from": time_to_ntp(datec1),
            "to": time_to_ntp(datec2),
            "times": {
                "from": time_to_ntp(timea),
                "to": time_to_ntp(timeb)
            }
        }
    }

    return single_lifecycle

@app.route("/")
def home():

    _now = datetime.datetime(2019, 4, 28, 14, 22)
    _to = datetime.datetime(2019, 4, 28, 17, 22)
    ret = time_to_resp([_now, _to])

    return jsonify(ret)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')