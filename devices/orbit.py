from typing import Annotated as A, Sequence, Dict

import numpy as np
from bluesky.protocols import Reading
from event_model import DataKey
from ophyd_async.core import (
    Array1D,
    StandardReadable,
    StandardReadableFormat as Format,
    SignalR,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from accml_lib.core.model.output.orbit import (
    BPMButtons,
    BPMPosition,
    BPMReading,
    Orbit as OrbitModel,
)


class RawOrbit(StandardReadable, EpicsDevice):
    # fmt:off
    names: A[ SignalR[ Sequence[str]       ], PvSuffix( "rdBpmNames" ), Format.CONFIG_SIGNAL   ] # noqa: F821
    #: currently missing in BESSY II twin, update pending
    # spos:  A[ SignalR[ Array1D[np.float64] ], PvSuffix( "rdSPos"     ), Format.CONFIG_SIGNAL   ] # noqa: F821

    count: A[ SignalR[ int                 ], PvSuffix( "count"      ), Format.UNCACHED_SIGNAL ] # noqa: F821

    rpos:  A[ SignalR[ Array1D[np.float64] ], PvSuffix( "rdPos"      ), Format.UNCACHED_SIGNAL ] # noqa: F821
    btns:  A[ SignalR[ Array1D[np.float64] ], PvSuffix( "rdButtons"  ), Format.UNCACHED_SIGNAL ] # noqa: F821
    # fmt:on


class Orbit(RawOrbit):
    """Provide read in data as orbit model"""

    async def describe(self) -> dict[str, DataKey]:
        d = await super().describe()
        d.pop(f"{self.name}-btns")
        rpos = d.pop(f"{self.name}-rpos")
        (L,) = rpos["shape"]
        assert L % 2 == 0
        d2 = {f"{self.name}-pos": DataKey(source="", shape=[], dtype="array")}
        d.update(d2)
        return d

    async def read(self) -> Dict[str, Reading]:
        data = await super().read()
        # todo: has ophyd / bluesky a helper func for splitting the read data?
        pos_pkg = data.pop(f"{self.name}-rpos")
        btn_pkg = data.pop(f"{self.name}-btns")
        names = await self.names.get_value()
        value = repack_bpm_data(pos_pkg, btn_pkg, names)
        pos = {
            f"{self.name}-pos": Reading(
                timestamp=pos_pkg["timestamp"], value=asdict(value)
            )
        }
        data.update(pos)
        return data


def repack_bpm_data(pos_pkg, btn_pkg, names: Sequence[str]) -> OrbitModel:
    pos = np.reshape(pos_pkg["value"], (-1, 2))
    btns = np.reshape(btn_pkg["value"], (-1, 4))
    return OrbitModel(
        orbit=[
            BPMReading(
                name=name,
                pos=BPMPosition(*p),
                btns=BPMButtons(*b),
            )
            for name, p, b in zip(names, pos, btns)
        ]
    )
