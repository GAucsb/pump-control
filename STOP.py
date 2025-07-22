from nesp_lib import Port
from nesp_lib.pump import Pump
from nesp_lib.exceptions import StateException

class NoVersionPump(Pump):
    def _Pump__firmware_version_get(self):
        self.version = (3, 61)
        return 100, (3, 61), 0

with Port('COM5') as port:
    pump_stock  = Pump(port, address=0)           # NE-1000
    pump_buffer = NoVersionPump(port, address=1)  # NE-1800

    for name, pump in [("Stock", pump_stock), ("Buffer", pump_buffer)]:
        try:
            pump.stop()
            print(f" {name} pump stopped.")
        except StateException:
            print(f" {name} pump already idle.")

