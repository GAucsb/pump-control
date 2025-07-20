from flask import Flask, render_template, request
from run_protocol import run_protocol  # Will update this later to match

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
        stock_conc        = float(request.form["stock_conc"])
        target_concs      = [float(c.strip()) for c in request.form["target_concs"].split(",")]

        prime_volume      = float(request.form["prime_volume"])
        prime_rate        = float(request.form["prime_rate"])
        device_volume     = float(request.form["device_volume"])

        num_stock_pump    = int(request.form["num_stock_pump"])
        num_buffer_pump   = int(request.form["num_buffer_pump"])

        residence_time    = float(request.form["residence_time"])
        flush_rate        = float(request.form["flush_rate"])

        flow_rate         = float(request.form["flow_rate"])
        hold_duration =     float(request.form["flow_time"]) * 60

        syringe_diameter  = float(request.form["syringe_diameter"])

        # The PRIME derived values
        prime_volume = prime_volume + device_volume
        prime_duration = prime_volume / prime_rate * 60  # seconds
        
        # The HOLD derived values (nothing yet)
        
        # The FLUSH derived values
        flush_volume = (residence_time * prime_volume) + device_volume
        flush_duration = flush_volume / flush_rate * 60


        run_protocol(
            stock_conc=stock_conc,
            target_concs=target_concs,
            prime_rate=prime_rate,
            hold_rate=flow_rate,
            flush_rate=flush_rate,
            flush_volume=flush_volume,
            flush_duration=flush_duration,
            syringe_diameter=syringe_diameter,
            num_stock_pump=num_stock_pump,
            num_buffer_pump=num_buffer_pump,
            prime_duration=prime_duration,
            hold_duration = hold_duration,
            prime_volume=prime_volume
        )

        
if __name__ == "__main__":
    app.run(debug=True)
