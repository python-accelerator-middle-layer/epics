"""

Todo:
    apply MAPE(-K) pattern

    The (long) knowledge should be rather be extracted
    by the supervisor using the data produced here

    add optimisation step to the run data
"""
import itertools
from typing import Sequence, Dict

from bluesky import plan_stubs as bps, preprocessors as bpp
from ophyd_async.core import Device, Signal
import logging

from accml.core.model.command import BehaviourOnError, Command
from accml.custom.epics.mexec.bluesky.utils import command_to_bps_mv_args

logger = logging.getLogger("accml")


def _correction_step_one(
    oracle,
    policy,
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
):
    # make the Measurement (the (M) in MAPE)
    measurement = yield from bps.trigger_and_read(detectors)
    # make the analysis part (the (A) in MAPE)
    # Todo: what is missing: do we actually need to do something
    #       that's the role of the analyser
    #       currently we always do
    dest = oracle.predict(measurement)
    # now we need to create  a plan  (the (P) in MAPE)
    plan = [
        Command(
            id=target.pc_name,
            # Todo: this must be handled in a more configurable fashion
            #       by a planner object?
            property="delta_set_current",
            value=target.delta_current,
            behaviour_on_error=BehaviourOnError.stop,
        )
        for target in dest
    ]
    # now execute the data  (the (E) in MAPE)
    tmp = [command_to_bps_mv_args(cmd, actuators) for cmd in plan]
    args = itertools.chain(*tmp)
    yield from bps.mv(*args)


def correction_steps_plan(
    oracle,
    policy,
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    info_signals: Dict[str, Signal],
    maximum_steps: int,
):
    all_dev = list(info_signals.values()) + list(detectors) + list(actuators.values())
    dev_name = info_signals["device_name"]
    ch_name = info_signals["channel_name"]
    ch_val = info_signals["channel_value"]

    for step in range(maximum_steps):
        yield from _correction_step_one(
            oracle=oracle, policy=policy, detectors=all_dev, actuators=actuators
        )
    # a final measurement at the end
    # or leave it to the user ?
    yield from bps.trigger_and_read(all_dev)


def correction_steps_execution_plan(
    oracle,
    policy,
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    info_signals: Dict[str, Signal],
    maximum_steps: int,
    md: None,
):
    """"""
    _md = md or dict()

    @bpp.stage_decorator(list(detectors) + list(actuators.values()))
    @bpp.run_decorator(md=_md)
    def inner():
        r = yield from correction_steps_plan(
            oracle=oracle,
            policy=policy,
            detectors=detectors,
            actuators=actuators,
            info_signals=info_signals,
            maximum_steps=maximum_steps,
        )
        return r

    r = yield from inner()
    return r
