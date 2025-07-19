from nesp_lib import Port, Pump, PumpingDirection
from nesp_lib.exceptions import StateException
import time

# Configuration
CYCLES = 1               # Number of push–pull cycles
DURATION = 60 * 2           # Seconds per push or pull phase
RATE = 5              # Pumping rate in mL/min
SYRINGE_DIAMETER = 14.5  # Syringe internal diameter in mm

# Calculate volume based on rate and duration
# (Rate in mL/min) × (Duration in min) = Volume in mL
VOLUME = RATE * (DURATION / 60.0)

# Open the serial port and configure both pumps
with Port('/dev/cu.PL2303G-USBtoUART210') as port:
    pump0 = Pump(port, address=0)
    pump1 = Pump(port, address=1)

    # Shared configuration: syringe diameter and rate
    for pump in [pump0, pump1]:
        pump.syringe_diameter = SYRINGE_DIAMETER
        pump.pumping_rate = RATE

    for i in range(CYCLES):
        print(f"\n🔁 Cycle {i + 1} - Phase 1: Pump 0 INFUSE, Pump 1 WITHDRAW")

        pump0.pumping_direction = PumpingDirection.INFUSE
        pump1.pumping_direction = PumpingDirection.WITHDRAW
        pump0.pumping_volume = VOLUME
        pump1.pumping_volume = VOLUME
        pump0.run(False)
        pump1.run(False)

        time.sleep(DURATION)

        try:
            pump0.stop()
        except StateException:
            pass

        try:
            pump1.stop()
        except StateException:
            pass

        time.sleep(0.5)

        print(f"🔁 Cycle {i + 1} - Phase 2: Pump 0 WITHDRAW, Pump 1 INFUSE")

        pump0.pumping_direction = PumpingDirection.WITHDRAW
        pump1.pumping_direction = PumpingDirection.INFUSE
        pump0.pumping_volume = VOLUME
        pump1.pumping_volume = VOLUME
        pump0.run(False)
        pump1.run(False)

        time.sleep(DURATION)

        try:
            pump0.stop()
        except StateException:
            pass

        try:
            pump1.stop()
        except StateException:
            pass

        time.sleep(0.5)

print("\n✅ Push–pull sequence complete.")
