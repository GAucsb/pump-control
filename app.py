from flask import Flask, render_template, request
from run_protocol import run_protocol  
import subprocess
from threading import Thread, Event



stop_event = Event()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run():
    try:
        # ── RAW USER INPUTS ────────────────────────────────────────────────
        stock_conc       = float(request.form["stock_conc"])
        target_concs     = [float(c.strip()) for c in request.form["target_concs"].split(",")]

        well_volume      = float(request.form["prime_volume"])     
        device_volume    = float(request.form["device_volume"])   
        prime_rate       = float(request.form["prime_rate"])

        residence_time   = float(request.form["residence_time"])
        flush_rate       = float(request.form["flush_rate"])

        flow_rate        = float(request.form["flow_rate"])
        hold_minutes     = float(request.form["flow_time"])

        syringe_diameter = float(request.form["syringe_diameter"])
        num_stock_pump   = int(request.form["num_stock_pump"])
        num_buffer_pump  = int(request.form["num_buffer_pump"])

        # ── DERIVED VALUES ────────────────────────────────────────────────
        prime_volume  = well_volume + device_volume                # mL  (already includes device)
        prime_duration = prime_volume / prime_rate * 60            # sec

        hold_duration  = hold_minutes * 60                         # sec

        flush_volume   = residence_time * prime_volume             # mL  ← no extra +device_volume
        flush_duration = flush_volume / flush_rate * 60            # sec

        stop_event.clear()
        Thread(target=run_protocol,args=
               
            (stock_conc, target_concs,
            prime_volume, prime_rate, prime_duration,
            flow_rate,  hold_duration,
            flush_rate, flush_volume, flush_duration,
            syringe_diameter, num_stock_pump, num_buffer_pump),
            
            kwargs={"stop_event": stop_event},daemon=True).start()
        

        return "Good"

    except Exception as e:
        return f"Error {e}"
    
@app.route("/stop", methods=["GET"])
def stop():
    # flip the flag; run_protocol will see it and stop pumps
    stop_event.set()
    return "<pre>Stop signal sent.</pre>"



if __name__ == "__main__":
    app.run(debug=True, threaded=True)

