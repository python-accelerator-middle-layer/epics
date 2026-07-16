from typing import Annotated as A, Sequence
import numpy as np
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from ophyd_async.core import (
    Array1D,
    StandardReadable,
    StandardReadableFormat as Format,
    SignalRW, SignalR,
)

class TurnByTurnDataConfig(StandardReadable, EpicsDevice):
    # fmt:off
    n_turns        : A[ SignalRW [ int                 ] , PvSuffix( "n_turns"        ), Format.UNCACHED_SIGNAL]  # noqa: F821
    run            : A[ SignalRW [ int                 ] , PvSuffix( "run"            ), Format.UNCACHED_SIGNAL]  # noqa: F821
    start_vec      : A[ SignalRW [ Array1D[np.float64] ] , PvSuffix( "start_vec"      ), Format.UNCACHED_SIGNAL]  # noqa: F821
    data_needed_at : A[ SignalR  [ Sequence[str]       ] , PvSuffix( "data_needed_at" ), Format.UNCACHED_SIGNAL]  # noqa: F821
    # fmt:on
