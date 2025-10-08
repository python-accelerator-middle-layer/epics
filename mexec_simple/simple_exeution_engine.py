"""

Todo:
    set up all the devices from the configuration
    I guess that is the use of the factory pattern?

"""
import asyncio
import logging
from typing import Sequence, Dict

from accml.core.interfaces.device_interface import SimpleReading, SimpleDevice
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.model.command import Command

logger = logging.getLogger("accml")


class SimpleMeasurementExecutionEngine(MeasurementExecutionEngine):


    def execute(
        self,
        commands: Sequence[Command],
        detectors: Sequence[SimpleDevice],
        actuators: Dict[str, SimpleDevice],
        md: Dict[str, object],

    ) -> str:
        """
        todo:
            for each command: treat it as an transactional plan of a single command or of many

            Review how to include transactional commands
        """
        assert self.async_loop is not None, "call setup first"

        logger.info("Executing commands:")

        all_dev = list(detectors) + list(actuators.values())
        unique_devs = list(set(all_dev))
        async def execute():
            await asyncio.gather( *(dev.stage() for dev in unique_devs) )
            try:
                r = await self._execute_all_commands(commands, all_dev, actuators, md)
            finally:
                await asyncio.gather(*(dev.unstage() for dev in unique_devs))
            return r
        self.async_loop.run_until_complete(execute())

    async def _execute_all_commands(
        self,
        commands: Sequence[Command],
        detectors: Sequence[SimpleDevice],
        actuators: Dict[str, SimpleDevice],
        md: Dict[str, object],

        ) -> str:

        for det in detectors:
            logger.info(f"  detector: {det.name}")

        # todo: handle data gathering
        async def execute_all():
            return [await self._execute_single(cmd, detectors, actuators) for cmd in commands]

        data = await execute_all()
        # store data to the data base / data lake / or file
        id_ = await self.store(data)
        return id_

    async def _execute_single(self, cmd: Command, detectors, actuators) -> dict[str, SimpleReading]:
        """
        1. step: find the devices and its associated methdds
        2. step: apply the set points to it
        3. read all the detector: yes all of them, whe have no filter here
        """
        logger.warning(f"Executing command {cmd}")
        actuator = actuators[cmd.id]
        channel = getattr(actuator, cmd.property)
        await channel.set(cmd.value)
        tmp = await asyncio.gather(*[d.read() for d in detectors])
        r = dict()
        for t in tmp:
            r.update(t)
        return r

    def setup(self, *args, async_loop=asyncio.get_event_loop()) -> None:
        self.async_loop = async_loop
        print("Setting up SimpleMeasurementExecutionEngine")

    async def store(self, data):
        data

    def __init__(self):
        self.async_loop = None

