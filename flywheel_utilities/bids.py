"""
BIDS related functions
"""

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, List

# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel.models.container_subject_output import (
        ContainerSubjectOutput,
    )  # type: ignore
    from flywheel_geartoolkit_context import GearToolkitContext  # type: ignore

# pylint: disable=wrong-import-position
from flywheel_utilities import utils

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


def add_dataset_description(bids_dir: Path) -> None:
    """
    Create dummy dataset_description.json as well as README.md

    Args:
        bids_dir: path to bids directory
    """

    # Dummy dataset description
    info = {
        "Acknowledgements": "",
        "Authors": ["dummy", "authors"],
        "BIDSVersion": "1.2.0",
        "DatasetDOI": "",
        "Funding": [],
        "HowToAcknowledge": "",
        "License": "",
        "Name": "dummy",
        "ReferencesAndLinks": [],
        "template": "project",
    }

    description = bids_dir / "dataset_description.json"

    if not description.is_file():

        with open(description, "w", encoding="utf-8") as data_description:
            json.dump(info, data_description, indent=4)

        log.info("Dummy dataset_description.json created " "in root bids directory")

    # Create dummy README
    readme = bids_dir / "README"

    with open(readme, "w", encoding="utf-8") as read_me:
        # Write some dummy lines so BIDS doesn't complain that it is too short
        read_me.write(150 * "Lorem ipsum\n")


def create_bids_dir(
    context: "GearToolkitContext",
    subject: "ContainerSubjectOutput",
    modalities: List[str],
    add_description: bool = True,
) -> Path:
    """
    Create BIDS directory, and a root level dummy dataset description if requested. The BIDS directory will maintain any
    session structure found on Flywheel.

    Args:
        context: gear context object
        subject: flywheel subject object
        modalities: list of modalities that need to be downloaded
        add_description: add dummy dataset description
    Return:
        bids_dir: path to bids directory
    """

    log.info("Creating bids directory structure...")

    # Determine number of sessions
    num_sessions = len(subject.sessions())
    log.info(f"Subject contains {num_sessions} sessions")

    sub_path: Path = context.work_dir / "bids" / ("sub-" + subject.label)

    for session in subject.sessions.iter():
        sesh_path = sub_path / ("ses-" + session.label)
        for folder in modalities:
            (sesh_path / folder).mkdir(parents=True, exist_ok=True)

    log.info(f"BIDS directory structure created in {context.work_dir}")

    if add_description:
        add_dataset_description(sub_path.parent)

    return sub_path.parent


def create_deriv_dir(
    context: "GearToolkitContext", sub_label: str, which_version: str = "first"
) -> Path:
    """
    Create output folder to store results. The folder name and version are retrieved from the manifest label and
    version. The folder structure follows the specification for BIDS derivatives (<pipeline>-v<version>).  E.g.,
    /fMRIPrep-v21.0.0/sub-XXXXX/

    Args:
        context: gear context object
        sub_label: subject label (XXXXXX)
        which_version: if using X.X.X_Y.Y.Y versioning, which position is the version of the underlying BIDS App.
        Specify single if only one version present, and specify none if no version is to be include

    Returns
        deriv_dir: path to derivatives folder
    """

    gear_name: str = utils.get_gear_name(context).replace(":", "-v")

    # Strip flywheel versioning to keep directory outputs same as those
    # produced by the standalone BIDs Apps
    if which_version != "none":
        if which_version == "first":
            search = r"(_[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})"
        elif which_version == "second":
            search = r"([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}_)"
        elif which_version == "single":
            search = r"([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})"

        result = re.search(search, gear_name)
        assert result is not None, (
            "Could not isolate Flywheel versioning in gear name when"
            " trying to strip it for BIDs derivative directory"
            f"Retrieved gear name: {gear_name}"
        )

        gear_name = re.sub(result.group(1), "", gear_name)

    else:
        gear_name = gear_name[: gear_name.find("-v")]

    deriv_dir: Path = context.work_dir / gear_name / ("sub-" + sub_label)

    deriv_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Created BIDs derivative directory: {deriv_dir}")

    return deriv_dir
