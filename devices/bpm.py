import asyncio
from typing import Annotated as A
import numpy as np
from bluesky.protocols import Triggerable, Status
from ophyd_async.core import (
    Array1D,
    StandardReadable,
    StandardReadableFormat as Format,
    SignalR, AsyncStatus,
)
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from accml.core.utils.ophyd_async.new_value import wait_for_new_value


class BPMTbTPosition(StandardReadable, EpicsDevice, Triggerable):
    """
    Todo:
        revisit if data should be exported in a data class
    """
    # fmt:off
    x   : A[SignalR[Array1D[np.float64]] , PvSuffix( "signals:tdp_synth:X"  ) , Format.UNCACHED_SIGNAL ]  # noqa: F821
    y   : A[SignalR[Array1D[np.float64]] , PvSuffix( "signals:tdp_synth:Y"  ) , Format.UNCACHED_SIGNAL ]  # noqa: F821
    sum : A[SignalR[Array1D[np.float64]] , PvSuffix( "signals:tdp_synth:SUM") , Format.UNCACHED_SIGNAL ]  # noqa: F821
    # fmt:on

    @AsyncStatus.wrap
    async def trigger(self) -> Status:
        """
        Todo: cross check with libera which variable is the last written
        """
        return await asyncio.gather(
            *[wait_for_new_value(sig, timeout=15.0) for sig in (self.x, self.y, self.sum)]
        )
