"""
Tag subjects with the gear and version number
"""

# pylint: disable=import-error
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
import logging
import sys

# Enable explicit type hints with mypy
from typing import TYPE_CHECKING

import flywheel  # type: ignore

if TYPE_CHECKING:
    from flywheel_geartoolkit_context import GearToolkitContext  # type: ignore
    from flywheel.models.container_subject_output import ContainerSubjectOutput  # type: ignore

from flywheel_utilities import utils

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


def update_subject_tags(
    context: "GearToolkitContext", subject: "ContainerSubjectOutput"
) -> None:
    """
    Update the subject's tag to indicate the gear has been run

    Args:
        context: gear context object
        subject: flywheel subject object
    """

    gear_name: str = utils.get_gear_name(context)

    if gear_name not in subject.tags:

        try:
            context.client.add_subject_tag(subject.id, gear_name)
        except flywheel.rest.ApiException as err:
            log.error(f"{err}")
            sys.exit(1)

        log.info(f"Subject's tags now include '{gear_name}'")
