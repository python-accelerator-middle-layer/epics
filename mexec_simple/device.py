from accml.core.interfaces.device_interface import SimpleDevice as SimpleDeviceInterface


class SimpleDeviceImpl(SimpleDeviceInterface):
    def __init__(self, *, name: str):
        self.name = name

    async def stage(self):
        pass

    async def unstage(self):
        pass