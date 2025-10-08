from accml.core.interfaces.device_interface import SimpleReading
from .device import SimpleDeviceImpl

from .signal import CaSignalR


class Tunes(SimpleDeviceImpl):
    def __init__(self, prefix: str, *, name: str):
        self.x = CaSignalR(prefix=f"{prefix}:x", name=f"{name}-x", use_new_value=True)
        self.y = CaSignalR(prefix=f"{prefix}:y", name=f"{name}-y", use_new_value=True)
        super().__init__(name=name)

    async def read(self) -> dict[str, dict[str, SimpleReading]]:
        return {
            self.name: dict(x=await self.x.read(), y=await self.y.read())
        }
