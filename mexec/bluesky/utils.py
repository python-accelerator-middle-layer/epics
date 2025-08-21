from typing import Sequence, Dict

from accml.core.model.command import Command
from ophyd_async.core import Device

def command_to_bps_mv_args(
    command: Command,
    actuators: Dict[str, Device],
):
    # first select the device
    t_device = actuators[command.id]
    channel = getattr(t_device, command.property)
    return channel, command.value