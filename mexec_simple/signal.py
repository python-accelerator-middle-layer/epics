import asyncio
import logging
import time

import aioca

from accml.core.interfaces.device_interface import SimpleStandardReadable, SimpleReading, SimpleMovable

logger = logging.getLogger("accml")


class CaSignalR(SimpleStandardReadable):
    """Read a standard signal using aioca
    """

    def __init__(self, *, prefix:str, name: str, use_new_value: bool = False):
        self.prefix = prefix
        self.name = name
        self.use_new_value = bool(use_new_value)

    async def _get_directly(self):
        try:
            r = await aioca.caget(self.prefix)
        except Exception as e:
            logger.error(f"{self.name}: failed to read EPICS signal {self.prefix}: {e}")
            raise e
        return r

    async def _get_new_value(self):
        fut = asyncio.get_event_loop().create_future()

        cnt = 0
        def cb(value):
            nonlocal cnt
            cnt += 1

            # First run returns immediately, don't use that one ....
            if not fut.done():
                logger.warning(f"{self.name}:{self.prefix} got new value {value} for {cnt=}")
                if cnt > 1:
                    fut.set_result(value)

        sub = None
        try:
            sub = aioca.camonitor(self.prefix, cb)
            r = await fut  # <-- wait here
        except Exception as e:
            logger.error(f"{self.name}: failed to read EPICS signal {self.prefix}: {e}")
            raise
        finally:
            if sub is not None:
                sub.close()

        return r

    async def get(self, wait_for_new_value=None):
        if wait_for_new_value is None:
            wait_for_new_value = self.use_new_value

        if wait_for_new_value:
            return await self._get_new_value()
        else:
            return await self._get_directly()

    async def read(self) -> dict[str, SimpleReading]:
        # Ensure that the time stamp is only run after the value is read
        v = await self.get()
        ts = time.time()
        return {self.name: dict(value=v, timestamp=ts)}


class CaSignalRW(CaSignalR, SimpleMovable):
    """Read and write a standard signal using aioca

    Deliberately a very simple signal. Not supporting that value is written to one variable
    and written back from another

    """
    async def set(self, value) -> None:
        await aioca.caput(self.prefix, value)
