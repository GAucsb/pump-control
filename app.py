from flask import Flask, render_template, request, redirect
from testing import run_protocol

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    try:
        run_protocol(
            stock_conc        = float(request.form["stock_conc"]),
            target_concs      = [float(c.strip()) for c in request.form["target_concs"].split(",")],
            prime_rate        = float(request.form["prime_rate"]),
            prime_volume      = float(request.form["prime_volume"]),
            hold_rate         = float(request.form["hold_rate"]),
            hold_duration_minutes = float(request.form["hold_duration"]),
            flush_rate        = float(request.form["flush_rate"]),
            flush_volume      = float(request.form["flush_volume"]),
            syringe_diameter  = float(request.form["syringe_diameter"]),
            tubing_length_cm  = float(request.form["tubing_length"]),
            tubing_diameter_cm= float(request.form["tubing_diameter"]),
            channel_volume    = float(request.form["channel_volume"])
        )
        return "✅ Protocol ran successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
