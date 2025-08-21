import functools
from dataclasses import asdict
from typing import Sequence, Dict

from bluesky import plan_stubs as bps, preprocessors as bpp
from ophyd_async.core import Device, Signal
import logging

from accml.core.model.command import Command

logger = logging.getLogger("accml")

def commands_plan(
    commands: Sequence[Command],
        detectors: Sequence[Device],
        actuators: Dict[str, Device],
        info_signals: Dict[str, Signal],
        repeat_readings: int = 1,
):
    """

    Inner plan for :func:`commands_execution_plan`

    Todo:
        Implement stop, ignore, rollback etc
        Device replace by ophyd_async.Settable
        info_signals as dataclass?
    """
    all_dev = list(info_signals.values()) + list(detectors) + list(actuators.values())
    dev_name = info_signals["device_name"]
    ch_name = info_signals["channel_name"]
    ch_val = info_signals["channel_value"]
    for command in commands:
        # first select the device
        t_device = actuators[command.id]
        channel = getattr(t_device, command.property)
        # then apply it to all
        yield from bps.mv(
            dev_name,
            str(command.id),
            ch_name,
            str(command.property),
            ch_val,
            command.value,
            channel,
            command.value,
        )
        # TODO: revisit how to address reading detectors
        #       also in the command language
        # read all devices
        # yield from bps.sleep(2.0)
        yield from bps.repeat(
            functools.partial(bps.trigger_and_read, all_dev),
            num=repeat_readings,
        )


def commands_execution_plan(
    commands: Sequence[Command],
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    info_signals: Dict[str, Signal],
    repeat_readings: int,
    md: None,
):
    """Translate commands to bluesky run-engine messages"""
    _md = md or dict()
    # CommandSequence nor Commands is json seriazable ....
    _md.update(dict(commands=[asdict(cmd) for cmd in commands]))

    @bpp.stage_decorator(list(detectors) + list(actuators.values()))
    @bpp.run_decorator(md=_md)
    def inner():
        r = yield from commands_plan(
            commands=commands,
            detectors=detectors,
            actuators=actuators,
            info_signals=info_signals,
            repeat_readings=repeat_readings,
        )
        return r

    r = yield from inner()
    return r
