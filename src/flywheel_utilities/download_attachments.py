"""
Download and unzip an attachment from the Flywheel project
"""

from __future__ import annotations

import logging
import re
import sys
from typing import TYPE_CHECKING

from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

if TYPE_CHECKING:
    from flywheel_geartoolkit_context import GearToolkitContext


logger = logging.getLogger()


def download_attachment(context: GearToolkitContext, name: str, is_dry_run: bool) -> None:
    """
    Download an attachment from the project and unzip into the working directory

    Parameters
    ----------
    context:
        Flywheel context manager
    name:
        name of attachment to be downloaded
    is_dry_run:
        results will not be unzipped if dry run
    """

    # Get the project
    proj_id: str = context.client.get_analysis(context.destination["id"])["parents"]["project"]
    proj = context.client.get_project(proj_id)

    # Search attachments for requested file
    for attach in proj.files:
        if not re.search(name, attach.name):
            continue

        logger.info(f"Located: {attach.name}")
        if not (context.work_dir / attach.name).is_file():
            attach.download(context.work_dir / attach.name)
        else:
            logger.debug("File already downloaded. Must be testing")
        break
    else:
        logger.error(f"Could not locate file using search term: {name}")
        sys.exit(1)

    # Unzip file
    # pylint: disable=undefined-loop-variable
    for ext in [".tar.gz", ".bz2", ".zip"]:
        if ext in attach.name:
            unzip_archive(context.work_dir / attach.name, context.work_dir, is_dry_run)
            break
