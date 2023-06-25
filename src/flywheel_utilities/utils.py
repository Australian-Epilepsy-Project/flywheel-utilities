"""
General functions.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flywheel_geartoolkit_context import GearToolkitContext


log = logging.getLogger(__name__)


def get_gear_name(context: GearToolkitContext) -> str:
    """
    Get gear name and version.

    Parameters
    ----------
    context:
        Flywheel gear context object

    Returns
    -------
    gear_name:
        <gear_name>:<version>
    """

    gear_name: str = context.manifest["label"]
    gear_name += ":"
    gear_name += context.manifest["version"]

    return gear_name


def zip_save_name(identifier: str, sub_label: str, dest_id: str) -> str:
    """
    Construct name of output zip file

    Parameters
    ----------
    identifier:
        base save name
    sub_label:
        subject label <sub-XXXXXX>
    dest_id:
        analysis destination ID

    Returns
    -------
        save name for zip file
    """

    save_name = identifier + "_"
    save_name += sub_label + "_" + dest_id

    return save_name + ".zip"
