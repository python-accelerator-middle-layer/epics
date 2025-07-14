from typing import Sequence

from pyaml.core.bl.liasion_translator_setup import load_managers
from .master_clock import MasterClock
from .multiplexer_for_settable_devices import MultiplexerProxy
from .power_converter import PowerConverter
from .tunes import Tunes
from ..local_facility.constants import special_pvs


def setup(device_ids: Sequence[str], prefix="Anonym:"):
    """

    device_ids: to cross check if device ids are instantiated

    """
    yp, _, __ = load_managers()

    quad_pcs = {name: PowerConverter(f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set") for
                name in yp.get("quadrupole_pcs")}

    quadrupoles = MultiplexerProxy(name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0])

    master_clock = MasterClock(f'{prefix}{special_pvs["master_clock"]}', name="mc")
    tunes = Tunes(f"{prefix}beam:twiss", name="tune")

    async def connect():
        await tunes.connect()
        r = await tunes.read()

    return dict(
        master_clock=master_clock, quadrupole_pcs=quadrupoles, tunes=tunes
    )
