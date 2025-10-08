from accml.core.interfaces.device_interface import SimpleStandardReadable, SimpleReading

import p4p
ctx = p4p.Context('pva')


class BeamPositionMonitor(SimpleStandardReadable):
    def __init__(self, *, name: str, prefix: str):
        self.name = name
        self.prefix = prefix

    async def read(self) -> dict[str, SimpleReading]:
        nt_data = ctx.read(f"{self.prefix}:pos")
        # convert nt_dsata to defined result
        r = convert(nt_data)
        return r
