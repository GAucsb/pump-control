from nesp_lib import Port, Pump, PumpingDirection
from nesp_lib.exceptions import StateException
import time
import math
from nesp_lib.pump import Pump

class NoVersionPump(Pump):
    def _Pump__firmware_version_get(self):
        self.version = (3, 61)  # Or whatever you want to label the NE-1800 with
        return 100, (3, 61), 0



def run_protocol(
    stock_conc,
    target_concs,
    prime_rate,
    prime_volume,
    hold_rate,
    hold_duration_minutes,
    flush_rate,
    flush_volume,
    syringe_diameter,
    tubing_length_cm,
    tubing_diameter_cm,
    channel_volume
):
    SECONDS = 60  # seconds per minute

    def tubing_volume():
        return (math.pi * (tubing_diameter_cm / 2) ** 2) * tubing_length_cm  # cm³ = mL

    def hold_volume():
        return hold_rate * (hold_duration_minutes * SECONDS)

    def sync_start(pump_slow, rate_slow, vol_slow, pump_fast, rate_fast, vol_fast):
        if rate_slow == 0 or rate_fast == 0:
            pump_slow.pumping_rate   = rate_slow
            pump_slow.pumping_volume = vol_slow
            pump_fast.pumping_rate   = rate_fast
            pump_fast.pumping_volume = vol_fast
            pump_slow.run(False)
            pump_fast.run(False)
            return

        t_slow = tubing_volume() / rate_slow * SECONDS
        t_fast = tubing_volume() / rate_fast * SECONDS
        dt  = abs(t_slow - t_fast)

        pump_slow.pumping_rate   = rate_slow
        pump_slow.pumping_volume = vol_slow
        pump_fast.pumping_rate   = rate_fast
        pump_fast.pumping_volume = vol_fast

        pump_slow.run(False)
        time.sleep(dt)
        pump_fast.run(False)

    def safe_sleep_from_flows(rate1, vol1, rate2, vol2):
        times = []
        if rate1 > 0:
            times.append(vol1 / rate1)
        if rate2 > 0:
            times.append(vol2 / rate2)
        if times:
            time.sleep(max(times) * SECONDS)

    with Port('/dev/cu.PL2303G-USBtoUART110') as port:
        pump_stock  = Pump(port, address=0)           # NE-1000
        pump_buffer = NoVersionPump(port, address=1)  # NE-1800

        # Basic hardware setup
        for p in (pump_stock, pump_buffer):
            p.syringe_diameter  = syringe_diameter
            p.pumping_direction = PumpingDirection.INFUSE

        # ── First concentration (prime ➜ hold)
        first_conc = target_concs[0]
        print(f"\n🧪 First concentration: {first_conc:.2f} mM SDS")

        f_stock  = first_conc / stock_conc
        f_buffer = 1 - f_stock

        # ----- PRIME -----
        rate_s = f_stock  * prime_rate
        rate_b = f_buffer * prime_rate
        vol_s  = f_stock  * prime_volume
        vol_b  = f_buffer * prime_volume

        if rate_s <= rate_b:
            sync_start(pump_stock,  rate_s, vol_s, pump_buffer, rate_b, vol_b)
        else:
            sync_start(pump_buffer, rate_b, vol_b, pump_stock,  rate_s, vol_s)

        safe_sleep_from_flows(rate_s, vol_s, rate_b, vol_b)
        for p in (pump_stock, pump_buffer):
            try: p.stop()
            except StateException: pass

        # ----- HOLD -----
        rate_s = f_stock  * hold_rate
        rate_b = f_buffer * hold_rate
        vol_s  = f_stock  * hold_volume()
        vol_b  = f_buffer * hold_volume()

        if rate_s <= rate_b:
            sync_start(pump_stock,  rate_s, vol_s, pump_buffer, rate_b, vol_b)
        else:
            sync_start(pump_buffer, rate_b, vol_b, pump_stock,  rate_s, vol_s)

        time.sleep(hold_duration_minutes * SECONDS)
        for p in (pump_stock, pump_buffer):
            try: p.stop()
            except StateException: pass

        # ── Remaining concentrations  (Flush ➜ Prime ➜ Hold)
        for target_conc in target_concs[1:]:
            print(f"\n🧪 Switching to {target_conc:.2f} mM SDS")

            f_stock  = target_conc / stock_conc
            f_buffer = 1 - f_stock

            # ===== FLUSH =====
            rate_s = f_stock  * flush_rate
            rate_b = f_buffer * flush_rate
            vol_s  = f_stock  * flush_volume
            vol_b  = f_buffer * flush_volume

            if rate_s <= rate_b:
                sync_start(pump_stock,  rate_s, vol_s, pump_buffer, rate_b, vol_b)
            else:
                sync_start(pump_buffer, rate_b, vol_b, pump_stock,  rate_s, vol_s)

            safe_sleep_from_flows(rate_s, vol_s, rate_b, vol_b)

            for p in (pump_stock, pump_buffer):
                try:
                    p.stop()
                except StateException:
                    pass

            # ===== PRIME =====
            rate_s = f_stock  * prime_rate
            rate_b = f_buffer * prime_rate
            vol_s  = f_stock  * prime_volume
            vol_b  = f_buffer * prime_volume

            if rate_s <= rate_b:
                sync_start(pump_stock,  rate_s, vol_s, pump_buffer, rate_b, vol_b)
            else:
                sync_start(pump_buffer, rate_b, vol_b, pump_stock,  rate_s, vol_s)

            safe_sleep_from_flows(rate_s, vol_s, rate_b, vol_b)
            for p in (pump_stock, pump_buffer):
                try: p.stop()
                except StateException: pass

            # ===== HOLD =====
            rate_s = f_stock  * hold_rate
            rate_b = f_buffer * hold_rate
            vol_s  = f_stock  * hold_volume()
            vol_b  = f_buffer * hold_volume()

            if rate_s <= rate_b:
                sync_start(pump_stock,  rate_s, vol_s, pump_buffer, rate_b, vol_b)
            else:
                sync_start(pump_buffer, rate_b, vol_b, pump_stock,  rate_s, vol_s)

            time.sleep(hold_duration_minutes * SECONDS)
            for p in (pump_stock, pump_buffer):
                try: p.stop()
                except StateException: pass

    print("\n✅ All steps completed.")
