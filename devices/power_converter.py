from accml.core.utils.ophyd_async.diff_channel import DiffChannel
from accml.core.utils.ophyd_async.multiplexer_for_settable_devices import _MultiplexerItemProxy
from accml.custom.epics.devices.utils import PVPositionerIsClose


class MultiplexerItemProxy(_MultiplexerItemProxy):
    """
    Todo:
        need to provide difference current
    """

    pass


class PowerConverter(PVPositionerIsClose):
    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.delta_set_current = DiffChannel(
                parent=self, name=f"{kwargs['name']}-diff-current"
            )
        super().__init__(*args, **kwargs)
