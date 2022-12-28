"""
General functions.
"""

import logging

# Enable explicit type hints with mypy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flywheel_geartoolkit_context import GearToolkitContext


log = logging.getLogger(__name__)


def get_gear_name(context: "GearToolkitContext") -> str:
    """
    Get gear name and version.

    Args:
        context: flywheel gear context object
    Returns:
        gear_name: <gear_name>:<version>
    """

    gear_name: str = context.manifest["label"]
    gear_name += ":"
    gear_name += context.manifest["version"]

    return gear_name


def zip_save_name(identifier: str, sub_label: str, dest_id: str) -> str:
    """
    Construct name of output zip file

    Args:
        identifier: base save name
        sub_label: subject label <sub-XXXXXX>
        dest_id: analysis destination ID
    """

    save_name = identifier + "_"
    save_name += sub_label + "_" + dest_id

    return save_name + ".zip"
