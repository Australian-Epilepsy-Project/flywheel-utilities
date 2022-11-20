'''
Install the freesurfer licence
'''

import logging
import os
from pathlib import Path

from typing import TYPE_CHECKING
# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel_geartoolkit_context import GearToolkitContext # type: ignore

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


def install_freesurfer_license(context: 'GearToolkitContext') -> None:
    '''
    Install Freesurfer license in correct position in $FREESURFER_HOME.  Assumes a license.txt file is uploaded at the
    project level

    Args:
        context: gear context object
    '''

    # Install path for license (at $FREESURFER_HOME)
    free_home = os.getenv('FREESURFER_HOME')
    assert free_home is not None, "Must set $FREESURFER_HOME before calling install_freesurfer_license()"

    fs_path = Path(free_home) / "license.txt"

    # Find the license file at the project level
    client = context.client
    proj_id = client.get_analysis(context.destination['id'])["parents"]["project"]

    proj = client.get_project(proj_id)

    if "FREESURFER_LICENSE" in proj["info"]:
        space_separated_text = proj["info"]["FREESURFER_LICENSE"]
        license_info = "\n".join(space_separated_text.split())

        log.info("Using FreeSurfer license in project info.")
    else:
        log.error("Freesurfer license.txt could not be located")
        log.error("Check the txt file is uploaded at the project level")
        log.error("Visit: https://docs.flywheel.io/hc/en-us/articles/"
                  "360013235453-How-to-include-a-Freesurfer-license-file"
                  "-in-order-to-run-a-Freesurfer-or-fMRIPrep-gear-")

        raise FileNotFoundError("Freesurfer license could not be located")

    # Write license to file
    with open(fs_path, "w", encoding='utf-8') as flp:
        flp.write(license_info)
        log.debug(f"License file written to {fs_path}")
