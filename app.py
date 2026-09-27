import PRT_API
from flask import Flask, json, render_template
from flask_sock import Sock
from datetime import datetime

app = Flask(__name__)

sock = Sock(app)

@app.route('/')
def home():
    api_key = "VtuM7TzcpsY8t6XMyAsPzcmAY"
    prt = PRT_API.PRT_API(api_key)
    
    result = prt.get_pred("7097")
    
    pred_time = result[0]['prdtm']
    return render_template('index.html', pred_time=pred_time)

@sock.route("/ws")
def tracker(ws):
    api_key = "VtuM7TzcpsY8t6XMyAsPzcmAY"
    json_return = []
    prt = PRT_API.PRT_API(api_key)
    while True:
        stop_id = ws.receive()
        # Don't track buses if there are none running between 2am and 5am
        if datetime.now().hour >= 2 and datetime.now().hour < 5:
            json_return.append([{"valid": False}])
            ws.send(json.dumps(json_return))
        elif(stop_id is not None and stop_id.isdigit()):
            result = prt.get_pred(int(stop_id))
            for bus in result:
                dt = datetime.strptime(bus['prdtm'], "%Y%m%d %H:%M:%S")
                ct = datetime.now()
                time_diff = dt - ct
                total_seconds = max(0, int(time_diff.total_seconds()))
                minute, second = divmod(total_seconds, 60)
                arrival_tm = datetime.strptime(bus['prdtm'], "%Y%m%d %H:%M:%S")
                json_return.append({"id": bus['id'], 
                                    "route_id": bus['rt'], 
                                    "minute": minute, 
                                    "second": second,
                                    "capacity": bus['psgld'],
                                    "arrival_tm": arrival_tm.strftime("%I:%M %p"),
                                    "valid": True})
            ws.send(json.dumps(json_return))

def main():
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()