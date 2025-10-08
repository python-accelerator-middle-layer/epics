from accml.core.interfaces.device_interface import SimpleDevice, SimpleMovable, ProvidesReferenceValue, SimpleReading, U
from .diff_channel import DiffChannel
from .signal import CaSignalRW, CaSignalR


class SimplePowerConverter(SimpleDevice, SimpleMovable, ProvidesReferenceValue):
    def __init__(self, *, prefix: str, name: str):
        self.reference_current = None
        self.setpoint = CaSignalRW(prefix=f"{prefix}:set", name=f"{name}-setpoint")
        self.readback = CaSignalR(prefix=f"{prefix}:rdbk", name=f"{name}-readback")
        self.delta_set_current = DiffChannel(parent=self, name=f"{name}-delta_set_current")
        self.name = name

    async def stage(self):
        assert self.reference_current is None, "reference_current already set! Did you forget to unstage?"

        # Simulate reading the reference current from the device
        self.reference_current = await self.setpoint.get()
        assert self.reference_current is not None, "Failed to read reference current"

    async def unstage(self):
        self.reference_current = None

    def get_current_value(self):
        # this rather BESSY II specific
        return self.setpoint.get()

    def get_reference_value(self):
        assert self.reference_current is not None
        return self.reference_current

    async def set(self, value) -> None:
        """
        Todo:
            review if a done signal should be implemented or similar
        """
        return await self.setpoint.set(value)

    async def read(self) -> dict[str, dict[str, SimpleReading]]:
        return {
            self.name: dict(
                setpoint=await self.setpoint.read(),
                readback=await self.readback.read(),
                delta_set_current=await self.delta_set_current.read(),
            )
        }