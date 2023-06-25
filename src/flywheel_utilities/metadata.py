"""
Tag subjects with the gear and version number
"""

from __future__ import annotations

import logging
import sys

# Enable explicit type hints with mypy
from typing import TYPE_CHECKING

import flywheel

from flywheel_utilities import utils

if TYPE_CHECKING:
    from flywheel.models.container_subject_output import ContainerSubjectOutput
    from flywheel_geartoolkit_context import GearToolkitContext


log = logging.getLogger(__name__)


def update_subject_tags(context: GearToolkitContext, subject: ContainerSubjectOutput) -> None:
    """
    Update the subject's tag to indicate the gear has been run

    Parameters
    ----------
    context:
        Flywheel gear context object
    subject:
        Flywheel subject object
    """

    gear_name: str = utils.get_gear_name(context)

    if gear_name not in subject.tags:
        try:
            context.client.add_subject_tag(subject.id, gear_name)
        except flywheel.rest.ApiException as err:  # pylint: disable=maybe-no-member
            log.error(f"{err}")
            sys.exit(1)

        log.info(f"Subject's tags now include '{gear_name}'")
