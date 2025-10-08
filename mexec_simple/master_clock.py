from accml.core.interfaces.device_interface import SimpleDevice, SimpleMovable, \
    ProvidesReferenceValue
from accml.custom.epics.mexec.diff_channel import DiffChannel
from accml.custom.epics.mexec_simple.signal import CaSignalRW


class MasterClock(SimpleDevice, SimpleMovable, ProvidesReferenceValue):
    """
    Warning:
            This code is not yet tested!
    """

    def __init__(self, *, prefix: str, name: str,  eps_rel=1e-6, eps_abs=1):
        self.prefix = prefix
        self.name = name

        self.frequency = CaSignalRW(prefix=prefix, name="f{name}-freq")
        self.reference_frequency = None
        self.diff_frequency = DiffChannel(parent=self, name=f"{name}-diff-freq")

    def get_reference_value(self):
        return self.reference_frequency

    async def stage(self):
        assert self.reference_frequency is None, "reference_frequency already set! Did you forget to unstage?"

        self.reference_frequency = await self.frequency.get()
        assert self.reference_frequency is not None, "Failed to read reference frequency"

    async def read(self):
        return {
            self.name: dict(
                frequency=await self.frequency.read(),
                reference_frequency=self.reference_frequency
            )
        }

    async def set(self, value) -> None:
        return await self.frequency.set(value)

    async def unstage(self):
        self.reference_frequency = None



