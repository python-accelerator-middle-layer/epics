import time
from typing import Union

from accml.core.interfaces.device_interface import SimpleMovable, SimpleStandardReadable, ProvidesReferenceValue


class DiffChannel(SimpleMovable):
    def __init__(
            self,
            *,
            name: str,
            parent: Union[SimpleStandardReadable, SimpleMovable, ProvidesReferenceValue],
    ):
        self.parent = parent
        self.name = name

    async def read(self) -> dict[str, dict[str, SimpleStandardReadable]]:
        v = await self.parent.get_current_value()
        dv = v - self.parent.get_reference_value()
        ts = time.time()
        return {self.name: dict(value=dv, timestamp=ts)}

    async def set(self, dv) -> None:
        v = self.parent.get_reference_value()
        value = dv + v
        return await self.parent.set(value)
