from nesp_lib import Port, Pump, PumpingDirection
from nesp_lib.exceptions import StateException
import time

# Temporary fallback for NE‑1800 compatibility
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
    num_buffer_pump,
    stop_event
):
    SECONDS = 60
    

    with Port("COM5") as port:
        pump_stock  = Pump(port, address=0)
        pump_buffer = NoVersionPump(port, address=1)

        for p in (pump_stock, pump_buffer):
            p.syringe_diameter  = syringe_diameter
            p.pumping_direction = PumpingDirection.INFUSE

        i = 0
        while i < len(target_concs):
            
            if stop_event.is_set():                # NEW
                try:
                    pump_stock.stop()
                    pump_buffer.stop()
                except StateException: 
                    pass
                print("Protocol aborted by user.")
                return
         
            conc = target_concs[i]
            f_stock  = conc / stock_conc
            f_buffer = 1 - f_stock

            print(f"\nConcentration Step {i + 1}  (target = {conc} mM)")

            # ─────────────────────────── PRIMING ──────────────────────────
            print("Priming")
            stock_rate   = f_stock  * prime_rate / num_stock_pump
            stock_volume = f_stock  * prime_volume
            buffer_rate  = f_buffer * prime_rate / num_buffer_pump
            buffer_volume= f_buffer * prime_volume

            if stock_rate > 0 and stock_volume > 0:
                pump_stock.pumping_rate   = stock_rate
                pump_stock.pumping_volume = stock_volume
                pump_stock.run(False)

            if buffer_rate > 0 and buffer_volume > 0:
                pump_buffer.pumping_rate   = buffer_rate
                pump_buffer.pumping_volume = buffer_volume
                pump_buffer.run(False)

            time.sleep(prime_duration)
            for p in (pump_stock, pump_buffer):
                try:
                    p.stop()
                except StateException:
                    pass

            # ─────────────────────────── HOLDING ──────────────────────────
            print("Holding")
            stock_rate   = f_stock  * hold_rate / num_stock_pump
            stock_volume = f_stock  * (hold_rate * hold_duration / SECONDS)
            buffer_rate  = f_buffer * hold_rate / num_buffer_pump
            buffer_volume= f_buffer * (hold_rate * hold_duration / SECONDS)

            if stock_rate > 0 and stock_volume > 0:
                pump_stock.pumping_rate   = stock_rate
                pump_stock.pumping_volume = stock_volume
                pump_stock.run(False)

            if buffer_rate > 0 and buffer_volume > 0:
                pump_buffer.pumping_rate   = buffer_rate
                pump_buffer.pumping_volume = buffer_volume
                pump_buffer.run(False)

            time.sleep(hold_duration)
            for p in (pump_stock, pump_buffer):
                try:
                    p.stop()
                except StateException:
                    pass

            # ─────────────────────────── FLUSHING ─────────────────────────
            if i < len(target_concs) - 1:
                next_conc      = target_concs[i + 1]
                next_f_stock   = next_conc / stock_conc
                next_f_buffer  = 1 - next_f_stock

                print("→ Flushing to next concentration")
                stock_rate   = next_f_stock  * flush_rate / num_stock_pump
                stock_volume = next_f_stock  * flush_volume
                buffer_rate  = next_f_buffer * flush_rate / num_buffer_pump
                buffer_volume= next_f_buffer * flush_volume

                if stock_rate > 0 and stock_volume > 0:
                    pump_stock.pumping_rate   = stock_rate
                    pump_stock.pumping_volume = stock_volume
                    pump_stock.run(False)

                if buffer_rate > 0 and buffer_volume > 0:
                    pump_buffer.pumping_rate   = buffer_rate
                    pump_buffer.pumping_volume = buffer_volume
                    pump_buffer.run(False)

                time.sleep(flush_duration)
                for p in (pump_stock, pump_buffer):
                    try:
                        p.stop()
                    except StateException:
                        pass

            i += 1

        print("\nComplete.")


# ───────────────────────── STOP FUNCTION  ─────────────────────
def stop_pumps():
    from nesp_lib.exceptions import StateException

    with Port("/dev/cu.PL2303G‑USBtoUART110") as port:
        pump_stock  = Pump(port, address=0)
        pump_buffer = NoVersionPump(port, address=1)

        for name, pump in (("Stock", pump_stock), ("Buffer", pump_buffer)):
            try:
                pump.stop()
                print(f"{name} pump stopped.")
            except StateException:
                print(f"{name} pump already idle.")
