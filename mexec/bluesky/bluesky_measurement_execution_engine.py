"""Demonstrator of a measurement execution engine

Todo:
    * implement full functionality

Missing features:

* handling behaviour_on_error
* how much of the accelerator access to wrap?
* hide devices behind a software multiplexer?
  In its current form quite some information will be stored
  in the databroker

"""
import logging
import os
from typing import Sequence, Dict

import numpy as np
from bluesky import RunEngine
from ophyd_async.core import Device, Signal

from accml.facility_specific_constants import special_pvs
from .correct_plan import correction_steps_execution_plan
from .execute_plan import commands_execution_plan
from ..devices.master_clock import MasterClock
from ..devices.multiplexer_for_settable_devices import MultiplexerProxy
from ..devices.power_converter import PowerConverter
from ..devices.tunes import Tunes


from accml.core.bl.liasion_translator_setup import load_managers
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.model.command import Command

logger = logging.getLogger("accml")


class OracleProxy:
    def __init__(self, oracle, data_keys: Sequence[str], targets: Sequence[float]):
        """
        Todo:
            base input data on data model
        """
        self.oracle = oracle
        self.data_keys = data_keys
        self.targets = np.asarray(targets)

    def predict(self, data: Dict[str, Dict[str, float]]):
        tmp = [data[key]["value"] for key in self.data_keys]
        tmp = np.array(tmp)
        delta = tmp - self.targets
        diff =  self.oracle.predict(*delta)
        return diff


class BlueskyMeasurementExecutionEngine(MeasurementExecutionEngine):
    """Demonstrator of a measurement engine as a bluesky runengine"""

    def __init__(self, run_engine: RunEngine):
        """

        Todo:
            Specify the device type
        """
        self.run_engine = run_engine

    def correction_step(self, *, oracle, policy, detectors, actuators, data_keys, targets,  **kwargs) -> str:
        oracle_proxy = OracleProxy(oracle=oracle, data_keys=data_keys, targets=targets)
        plan = correction_steps_execution_plan(
            oracle=oracle_proxy,
            policy=policy,
            detectors=detectors,
            actuators=actuators,
            maximum_steps=1,
            **kwargs
        )
        (uid,) = self.run_engine(plan)
        return uid


    def execute(
        self,
        commands_collection: Sequence[Sequence[Command]],
        repeat_readings: int,
        detectors: Sequence[Device],
        actuators: Dict[str, Device],
        info_signals: Dict[str, Signal],
        md: Dict[str, object],
    ) -> str:
        plan = commands_execution_plan(
            commands=commands_collection,
            detectors=detectors,
            actuators=actuators,
            info_signals=info_signals,
            repeat_readings=repeat_readings,
            md=md,
        )
        (uid,) = self.run_engine(plan)
        return uid

    def setup(self, *args) -> None:
        """
        Setup the measurement execution engine

        Todo:
            make prefix an overridable variable
        """
        prefix = os.environ.get("USER", "Anonym") + ":"
        yp, _, __ = load_managers()

        quad_pcs = {
            name: PowerConverter(
                f"{prefix}{name}:",
                name=name,
                readback_suffix="rdbk",
                setpoint_suffix="set",
            )
            for name in yp.get("quadrupole_pcs")
        }

        quadrupoles = MultiplexerProxy(
            name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0]
        )

        master_clock = MasterClock(f'{prefix}{special_pvs["master_clock"]}', name="mc")
        tunes = Tunes(f"{prefix}TUNECC", name="tune")

        async def connect():
            await tunes.connect()
            r = await tunes.read()

        return dict(master_clock=master_clock, quadrupole_pcs=quadrupoles, tunes=tunes)
