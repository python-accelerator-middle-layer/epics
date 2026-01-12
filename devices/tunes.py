import time

import jsons
from bluesky.protocols import Reading
from event_model import DataKey
from ophyd_async.core import StandardReadable, AsyncStatus
from ophyd_async.epics.core import epics_signal_r

from accml.app.tune.model import Tune
from accml.core.utils.ophyd_async.new_value import wait_for_new_value


class TuneSignal(StandardReadable):
    def __init__(self, prefix, *, name: str):
        with self.add_children_as_readables():
            self.sig = epics_signal_r(float, f"{prefix}")
        super().__init__(name=name)

    @AsyncStatus.wrap
    async def read(self) -> dict[str, Reading]:
        #: on real machine timeout of 5 was too small
        await wait_for_new_value(self.sig, timeout=8)
        return await super().read()

class TunesTransversal(StandardReadable):
    def __init__(self, prefix, *, name):
        with self.add_children_as_readables():
            self.x = TuneSignal(f"{prefix}:rdH", name=f"{name}-x")
            self.y = TuneSignal(f"{prefix}:rdV", name=f"{name}-y")
        super().__init__(name=name)

    async def describe(self) -> dict[str, DataKey]:
        tmp = await super().describe()
        d = {
             self.name: dict(shape=[], dtype="array", source=""),
        }
        r = {**tmp, **d}
        return r

    @AsyncStatus.wrap
    async def read(self) -> dict[str, Reading]:
        tmp =  await super().read()
        x = tmp[f"{self.name}-x-sig"]
        y = tmp[f"{self.name}-y-sig"]
        # timestamps often allow no add but sub ...
        # therefore this extra turn
        dt = y["timestamp"] - x["timestamp"]
        severity = max(x["alarm_severity"], y["alarm_severity"])
        # return a proper data model here!
        d = {
            self.name : dict(
                value=jsons.dump(Tune(x=x["value"], y=y["value"])),
                timestamp=x["timestamp"] + dt/2.0,
                alarm_severity=severity
            )
        }
        r =  {**tmp, **d}
        return r


class Tunes(StandardReadable):
    def __init__(self, prefix, *, name):
        with self.add_children_as_readables():
            self.transversal = TunesTransversal(prefix, name=f"{name}-transversal")
        super().__init__(name=name)

