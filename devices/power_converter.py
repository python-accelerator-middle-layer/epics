from accml.custom.epics.devices.utils import PVPositionerIsClose


class PowerConverter(PVPositionerIsClose):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, item):
        if item == "set_current":
            return self.setpoint
        raise AssertionError("don't know how to handle set point", item)
