"""
Simple wrappers to use Flywheel.
- get_subject()
- check_run_level()
"""

import logging
import sys
from typing import TYPE_CHECKING

import flywheel

# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel.models.container_subject_output import ContainerSubjectOutput
    from flywheel_geartoolkit_context import GearToolkitContext


log = logging.getLogger(__name__)


def get_subject(context: "GearToolkitContext") -> "ContainerSubjectOutput":
    """
    Retrieve flywheel subject object

    Args:
        context: gear context object
    Returns:
        subject: flywheel subject object
    """

    destination = context.client.get(context.destination["id"])
    subject = context.client.get(destination.parent["id"])

    log.info(f"Subject {subject.label} retrieved")

    return subject


def check_run_level(
    context: "GearToolkitContext", which_level: str, gear_type: str = "analysis"
) -> None:
    """
    Check at which level the gear is being run and cross check with the supplied which_level string.
    By default, the gear will also be checked that it is running at the analysis level.
    This can be overridden via the gear_type argument.

    Args:
        context: gear context object
        which_level: which level should the gear be run at
        gear_type: analysis or utility gear
    """

    try:
        destination = context.client.get(context.destination["id"])
    except flywheel.ApiException as err:  # pylint: disable=maybe-no-member
        log.error("The destination id does not point to a valid analysis container")
        log.error(f"{err}")
        sys.exit(1)

    if destination.container_type != gear_type:
        log.error("The destination ID does not point to a valid " f"{gear_type} container")
        sys.exit(1)

    if destination.parent.type != which_level:
        log.error(f"Destination type is {destination.parent.type}")
        log.error(f"Expected {which_level}")
        sys.exit(1)
