from ophyd_async.epics.core import epics_signal_rw, epics_signal_r

from accml.core.utils.ophyd_async.pv_positioner_like_utils import _SettableControllingDifference


class PVPositionerIsClose(_SettableControllingDifference):
    """a power converter that allows overriding setpoint and readback suffix"""

    def __init__(
        self,
        prefix: str,
        setpoint_suffix: str = None,
        readback_suffix: str = None,
        name="",
        **kwargs,
    ):
        assert readback_suffix is not None
        assert setpoint_suffix is not None

        with self.add_children_as_readables():
            # Todo: add hints
            # fmt:off
            self.setpoint  = epics_signal_rw ( float , f"ca://{prefix}{setpoint_suffix}"     , name="set"  )
            self.readback  = epics_signal_r  ( float , f"ca://{prefix}{readback_suffix}"     , name="rdbk" )
            self.units     = epics_signal_r  ( str   , f"ca://{prefix}{readback_suffix}.EGU",  name="units")
            self.precision = epics_signal_r  ( int   , f"ca://{prefix}{readback_suffix}.PREC", name="prec" )
            # fmt:on

        super().__init__(name=name, **kwargs)
