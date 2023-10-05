"""
Install the freesurfer licence
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import flywheel
    from flywheel_geartoolkit_context import GearToolkitContext

log = logging.getLogger(__name__)


def install_freesurfer_license(context: GearToolkitContext) -> None:
    """
    Install Freesurfer license in correct position in $FREESURFER_HOME.
    This assumes the Freesurfer license information is stored at the project level in the
    "Custom Information" section as a string.

    Parameters
    ----------
    context:
        FLywheel gear context object
    """

    # Install path for license (at $FREESURFER_HOME)
    free_home: Optional[str] = os.getenv("FREESURFER_HOME")
    assert (
        free_home is not None
    ), "Must set $FREESURFER_HOME before calling install_freesurfer_license()"

    fs_path: Path = Path(free_home) / "license.txt"

    # Find the license file at the project level
    client: flywheel.Client = context.client
    proj_id: str = client.get_analysis(context.destination["id"])["parents"]["project"]

    proj: flywheel.models.project.Project = client.get_project(proj_id)

    if "FREESURFER_LICENSE" in proj["info"]:
        space_separated_text: str = proj["info"]["FREESURFER_LICENSE"]
        license_info: str = "\n".join(space_separated_text.split())

        log.info("Using FreeSurfer license in project info.")
    else:
        log.error("Freesurfer license information could not be located")
        log.error("Check the information is uploaded at the project level")
        log.error('Must be in "Custom Information" as a string with:')
        log.error('\t the key set to "FREESURFER_LICENSE"')
        log.error("\t the value set to the contents of license.txt")

        raise FileNotFoundError("Freesurfer license could not be located")

    # Write license to file
    with open(fs_path, "w", encoding="utf-8") as flp:
        flp.write(license_info)
        log.debug(f"License file written to {fs_path}")
