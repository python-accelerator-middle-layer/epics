from accml.core.utils.ophyd_async.multiplexer_for_settable_devices import (
    _MultiplexerItemProxy,
)
from accml.custom.epics.devices.utils import PVPositionerIsClose


class MultiplexerItemProxy(_MultiplexerItemProxy):
    """
    Todo:
        need to provide difference current

        I guess it can be removed as delta_backend handles this part already
    """

    pass


class PowerConverter(PVPositionerIsClose):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, item):
        if item == "set_current":
            return self.setpoint
        raise AssertionError("don't know how to handle set point", item)
