from nesp_lib import Port, Pump, PumpingDirection
from nesp_lib.exceptions import StateException
import time

# Temporary fallback for NE-1800 compatibility
class NoVersionPump(Pump):
    def _Pump__firmware_version_get(self):
        self.version = (3, 61)
        return 100, (3, 61), 0

def run_protocol(
    stock_conc,
    target_concs,
    prime_volume,
    prime_rate,
    prime_duration,
    hold_rate,
    hold_duration,
    flush_rate,
    flush_volume,
    flush_duration,
    syringe_diameter,
    num_stock_pump,
    num_buffer_pump
):
    SECONDS = 60

    with Port('/dev/cu.PL2303G-USBtoUART110') as port:
        # Setup pumps
        pump_stock = Pump(port, address=0)
        pump_buffer = NoVersionPump(port, address=1)

        for pump in [pump_stock, pump_buffer]:
            pump.syringe_diameter = syringe_diameter
            pump.pumping_direction = PumpingDirection.INFUSE

        i = 0
        while i < len(target_concs):
            conc = target_concs[i]
            f_stock = conc / stock_conc
            f_buffer = 1 - f_stock

            print(f"\n Concentration Step {i+1}")

            
            print("Priming")
            pump_stock.pumping_rate = f_stock * prime_rate / num_stock_pump
            pump_stock.pumping_volume = f_stock * prime_volume
            pump_buffer.pumping_rate = f_buffer * prime_rate / num_buffer_pump
            pump_buffer.pumping_volume = f_buffer * prime_volume

            pump_stock.run(False)
            pump_buffer.run(False)
            time.sleep(prime_duration)
            for p in (pump_stock, pump_buffer):
                try:
                    p.stop()
                except StateException:
                    pass

            
            print(" Holding")
            pump_stock.pumping_rate = f_stock * hold_rate / num_stock_pump
            pump_stock.pumping_volume = f_stock * (hold_rate * hold_duration / SECONDS)
            pump_buffer.pumping_rate = f_buffer * hold_rate / num_buffer_pump
            pump_buffer.pumping_volume = f_buffer * (hold_rate * hold_duration / SECONDS)

            pump_stock.run(False)
            pump_buffer.run(False)
            time.sleep(hold_duration)
            for p in (pump_stock, pump_buffer):
                try: p.stop()
                except StateException: pass

            
            if i < len(target_concs) - 1:
                next_conc = target_concs[i + 1]
                next_f_stock = next_conc / stock_conc
                next_f_buffer = 1 - next_f_stock

                print("→ Flushing")
                pump_stock.pumping_rate = next_f_stock * flush_rate / num_stock_pump
                pump_stock.pumping_volume = next_f_stock * flush_volume
                pump_buffer.pumping_rate = next_f_buffer * flush_rate / num_buffer_pump
                pump_buffer.pumping_volume = next_f_buffer * flush_volume

                pump_stock.run(False)
                pump_buffer.run(False)
                time.sleep(flush_duration)
                for p in (pump_stock, pump_buffer):
                    try: p.stop()
                    except StateException: pass

            i += 1

        print("\n Complete.")
