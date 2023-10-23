This README file explains how to get the watchdog reset status and how to
inject it into `iot2050-event-record` service.

# How to get the watchdog reset status?

The `wdt_example.py` below shows how to get the watchdog reset status.

```py
import psutil
import time
from datetime import datetime

WDIOF_CARDRESET = "32"
WDT_PATH = "/sys/class/watchdog/watchdog0/bootstatus"

EVENT_STRINGS = {
    "wdt": "{} watchdog reset is detected",
    "no-wdt": "{} watchdog reset isn't detected"
}

def record_wdt_events():
    status = ""
    with open(WDT_PATH, "r") as f:
        status = f.read().strip()

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    if WDIOF_CARDRESET == status:
        print(EVENT_STRINGS["wdt"].format(boot_time))
    else:
        print(EVENT_STRINGS["no-wdt"].format(boot_time))

if __name__ == "__main__":
    record_wdt_events()
```

# How to inject it into iot2050-event-record?

Please refer to [README.md](./README.md).
