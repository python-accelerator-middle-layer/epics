import asyncio
import time
from dataclasses import dataclass

import aioca

from accml.core.interfaces.device_interface import SimpleStandardReadable, SimpleMovable, SimpleReading


@dataclass
class Channel:
    channel_name: str
    timeout: float

@dataclass
class ReadWriteable:
    read: Channel
    write: Channel


class SimpleSettableDevice(SimpleStandardReadable, SimpleMovable):
    def __init__(self, *, name: str, setpoint: str, readback: str, set_timeout=1, read_timeout=1):
        self.name = name
        self.setpoint = setpoint
        self.readback = readback
        self.read_timeout = read_timeout
        self.set_timeout = set_timeout

    async def read(self) -> dict[str, SimpleReading]:
        setp = await asyncio.wait_for(aioca.caget(f"{self.setpoint}"), timeout=self.read_timeout)
        rdbk = await asyncio.wait_for(aioca.caget(f"{self.setpoint}"), timeout=self.read_timeout)
        return dict(
            # Todo: fix that timestamp of IOC is used
            setpoint=SimpleReading(timestamp=time.time(), value=setp),
            readback=SimpleReading(timestamp=time.time(), value=rdbk)
        )

    async def set(self, val) -> None:
        r = await asyncio.wait_for(aioca.caput(f"{self.setpoint}", val), timeout=self.set_timeout)
        return r
