"""
check_pumps.py  ―  Quick probe for NE‑1000 / NE‑1800 pumps on addresses 0 and 1.

Usage:
    python check_pumps.py

Adjust PORT and BAUD if needed.
"""

from nesp_lib import Port, Pump
from nesp_lib.exceptions import InternalException
import sys, time

PORT = "/dev/tty.PL2303G-USBtoUART110"   # <- Adjust if needed
BAUD = 9600                              # <- Match pump settings
ADDRESSES_TO_TEST = (0, 1)

# 🔧 Subclass that bypasses the firmware version check (for NE-1800 or weird versions)
class NoVersionPump(Pump):
    def _Pump__firmware_version_get(self):
        self.version = (3, 61)  # Set something safe-ish
        return 100, (3, 61), 0

def probe(port, addr) -> bool:
    """
    Try to instantiate a Pump at `addr`. Fall back to NoVersionPump if needed.
    Returns True if a pump responds.
    """
    try:
        print(f"🔎  Trying address {addr} … ", end="", flush=True)
        pump = Pump(port, address=addr)
        print(f"✅  Detected!  Firmware: {pump.firmware_version}")
        return True

    except InternalException:
        print("⚠️  Pump responded, but nesp_lib couldn’t parse the firmware string.")
        print("   ⟳ Trying with NoVersionPump… ", end="", flush=True)
        try:
            pump = NoVersionPump(port, address=addr)
            print(f"✅  Connected via NoVersionPump! Firmware bypassed.")
            return True
        except Exception as e:
            print(f"❌  Failed fallback: {type(e).__name__}: {e}")
            return False

    except Exception as e:
        print(f"❌  No pump detected ({type(e).__name__}: {e})")
        return False

def main() -> None:
    found_any = False

    try:
        with Port(PORT, baud_rate=BAUD) as port:
            time.sleep(1)  # Let line stabilize
            for addr in ADDRESSES_TO_TEST:
                if probe(port, addr):
                    found_any = True

    except Exception as e:
        sys.exit(f"\n❌ Failed to open port {PORT}: {e}")

    if not found_any:
        sys.exit("\nNo pumps detected on the tested addresses.")
    else:
        print("\n🎉  Probe finished.")

if __name__ == "__main__":
    main()
