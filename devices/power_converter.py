import time
from typing import Unpack

import aioca

from accml.core.interfaces.device_interface import SimpleStandardReadable, SimpleMovable, T_co, SimpleReading

class PowerConverter(SimpleStandardReadable, SimpleMovable):
    """
    Todo:
        need to have a generic class we derive from ...
    """

    def __init__(self, *, name: str, prefix: str):
        self.name = name
        self.prefix = prefix

    async def read(self) -> dict[str, SimpleReading]:
        return dict(
            # Todo: fix that timestamp of IOC is used
            setpoint=SimpleReading(timestamp=time.time(), value=await aioca.caget(f"{self.prefix}:setpoint")),
            readback=SimpleReading(timestamp=time.time(), value=await aioca.caget(f"{self.prefix}:setpoint"))
        )

    async def set(self, *args: Unpack[tuple[T_co]]) -> None:
        r = await aioca.caput(f"{self.prefix}:setpoint", args[0])
        return r
