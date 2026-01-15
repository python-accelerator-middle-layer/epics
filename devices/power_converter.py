from accml.custom.epics.devices.utils import PVPositionerIsClose


class PowerConverter(PVPositionerIsClose):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_current = self.setpoint
