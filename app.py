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
    prt = PRT_API.PRT_API(api_key)
    while True:
        if(ws.receive()):
            result = prt.get_pred("7097")
            json_return = []
            for bus in result:
                dt = datetime.strptime(bus['prdtm'], "%Y%m%d %H:%M:%S")
                ct = datetime.now()
                time_diff = dt - ct
                total_seconds = max(0, int(time_diff.total_seconds()))
                minute, second = divmod(total_seconds, 60)
                json_return.append({"id": bus['id'], 
                                    "route_id": bus['rt'], 
                                    "minute": minute, 
                                    "second": second,
                                    "capacity": bus['psgld']})
            ws.send(json.dumps(json_return))

def main():
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()