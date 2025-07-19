from nesp_lib import Port, Pump, PumpingDirection
from nesp_lib.exceptions import StateException
import time

# STATIC VARIABLES 
SECONDS = 60


SYRINGE_DIAMETER = 14.5  # Syringe internal diameter in mm
STOCK_CONC = 0.2         # mM SDS
CHANNEL_VOLUME = 1.0     # mL
FLUSH_MULTIPLIER = 3     # Multiplier for flush volume

##
PRIME_VOLUME = 0.2
PRIME_FLOW_RATE = 0.05
PRIME_DURATION = PRIME_VOLUME / PRIME_FLOW_RATE * SECONDS

###
HOLD_FLOW_RATE = 0.05
HOLD_DURATION = 10 * SECONDS
HOLD_VOLUME = HOLD_FLOW_RATE * (HOLD_DURATION / SECONDS)
### 

FLUSH_VOLUME = CHANNEL_VOLUME * FLUSH_MULTIPLIER
FLUSH_FLOW_RATE = 0.05
FLUSH_DURATION = FLUSH_VOLUME / FLUSH_FLOW_RATE * SECONDS

TARGET_CONCS = [0.01, 0.05, 0.1, 0.5, 1.0]

# Open serial port
with Port('/dev/tty.PL2303G-USBtoUART110') as port:
    pump_stock = Pump(port, address=0)
    pump_buffer = Pump(port, address=1)

    pump_stock.syringe_diameter = SYRINGE_DIAMETER
    pump_stock.pumping_direction = PumpingDirection.INFUSE

    pump_buffer.syringe_diameter = SYRINGE_DIAMETER
    pump_buffer.pumping_direction = PumpingDirection.INFUSE

   
    # FIRST CONCENTRATION: 0.01 mM SDS
   
    print("test")
    target_conc = 0.01
    f_stock = target_conc / STOCK_CONC
    f_buffer = 1 - f_stock

    # Prime
    print(f" Prining  ")
    pump_stock.pumping_rate = f_stock * PRIME_FLOW_RATE
    pump_buffer.pumping_rate = f_buffer * PRIME_FLOW_RATE
    pump_stock.pumping_volume = f_stock * PRIME_VOLUME
    pump_buffer.pumping_volume = f_buffer * PRIME_VOLUME

    pump_stock.run(False)
    pump_buffer.run(False)
    time.sleep(PRIME_DURATION)

    try:
        pump_stock.stop()
    except StateException:
        pass
    try:
        pump_buffer.stop()
    except StateException:
        pass

    # Hold
    print(f" Holding")
    pump_stock.pumping_rate = f_stock * HOLD_FLOW_RATE
    pump_buffer.pumping_rate = f_buffer * HOLD_FLOW_RATE
    pump_stock.pumping_volume = f_stock * HOLD_VOLUME
    pump_buffer.pumping_volume = f_buffer * HOLD_VOLUME

    pump_stock.run(False)
    pump_buffer.run(False)
    time.sleep(HOLD_DURATION)

    try:
        pump_stock.stop()
    except StateException:
        pass
    try:
        pump_buffer.stop()
    except StateException:
        pass

    # Loops
    for target_conc in [0.05, 0.1, 0.5, 1.0]:
        print(f"\n🧪 Next concentration: {target_conc} mM SDS")
        f_stock = target_conc / STOCK_CONC
        f_buffer = 1 - f_stock

        # Flush
        print(f"FLUSHING")
        pump_stock.pumping_rate = f_stock * FLUSH_FLOW_RATE
        pump_buffer.pumping_rate = f_buffer * FLUSH_FLOW_RATE
        pump_stock.pumping_volume = f_stock * FLUSH_VOLUME
        pump_buffer.pumping_volume = f_buffer * FLUSH_VOLUME

        pump_stock.run(False)
        pump_buffer.run(False)
        time.sleep(FLUSH_DURATION)

        try:
            pump_stock.stop()
        except StateException:
            pass
        try:
            pump_buffer.stop()
        except StateException:
            pass

        # Prime
        print(f"Primneing")
        pump_stock.pumping_rate = f_stock * PRIME_FLOW_RATE
        pump_buffer.pumping_rate = f_buffer * PRIME_FLOW_RATE
        pump_stock.pumping_volume = f_stock * PRIME_VOLUME
        pump_buffer.pumping_volume = f_buffer * PRIME_VOLUME

        pump_stock.run(False)
        pump_buffer.run(False)
        time.sleep(PRIME_DURATION)

        try:
            pump_stock.stop()
        except StateException:
            pass
        try:
            pump_buffer.stop()
        except StateException:
            pass

        # Hold
        print(f"  ⏳ Holding for 10 minutes at 0.1 mL/min")
        pump_stock.pumping_rate = f_stock * HOLD_FLOW_RATE
        pump_buffer.pumping_rate = f_buffer * HOLD_FLOW_RATE
        pump_stock.pumping_volume = f_stock * HOLD_VOLUME
        pump_buffer.pumping_volume = f_buffer * HOLD_VOLUME

        pump_stock.run(False)
        pump_buffer.run(False)
        time.sleep(HOLD_DURATION)

        try:
            pump_stock.stop()
        except StateException:
            pass
        try:
            pump_buffer.stop()
        except StateException:
            pass

print("\n✅ All steps completed.")
