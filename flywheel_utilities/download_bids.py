"""
Module for downloading bids data from flywheel
"""

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel.models.container_acquisition_output import (
        ContainerAcquisitionOutput,
    )
    from flywheel.models.container_subject_output import (
        ContainerSubjectOutput,
    )
    from flywheel.models.file_entry import FileEntry

log = logging.getLogger(__name__)


# pylint: disable=too-many-locals
# pylint: disable=too-many-return-statements
def populate_intended_for(fw_file: "FileEntry", sidecar: Path) -> None:
    """
    The json sidecars stored on Flywheel do not have the IntendedFor field populated. Instead, this information is
    found in the metadata.
    Args:
        fw_file: json sidecar file on Flywheel
        sidecar: path to saved json sidecar
    """

    log.debug(f"Populating IntendedFor of: {sidecar}")

    # Retrieve IntendedFor information from metadata
    intended_for_orig: List[str] = fw_file["info"]["IntendedFor"]

    if not intended_for_orig:
        log.warning("Original IntendedFor field in metadata empty")
        log.warning(f"file: {fw_file.name}")

    # IntendedFor fields in the metadata can contain ALL files from the specified folder (typically func)
    # Filter to only leave NIfTI files
    intended_for = []
    for field in intended_for_orig:
        if field.endswith(".nii.gz") or field.endswith(".nii"):
            intended_for.append(field)

    if not intended_for:
        log.warning("Filtered IntendedFor field empty")

    # Read in downloaded sidecar and update the IntendedFor field
    with open(sidecar, "r", encoding="utf-8") as in_json:
        json_decoded = json.load(in_json)

    json_decoded["IntendedFor"] = intended_for

    with open(sidecar, "w", encoding="utf-8") as out_json:
        json.dump(json_decoded, out_json, sort_keys=True, indent=2)


def post_populate_intended_for(dir_sub: Path, post_populate) -> None:
    """
    The json sidecars stored on Flywheel do not have the IntendedFor field populated. Instead, this information is
    found in the metadata. By default the IntendedFor fields with be populated with this information. This function
    allows one to specify the modalities containing files that the fmaps should be used for.
    E.g., supplying ['dwi', 'func'] will result in the IntendedFor fields containing all NIfTI files from the dwi and
    func folder. This argument must be passed to `download_modalities`.

    Args:
        dir_sub: subject's BIDS directory
        post_populate: populate IntendedFor fields with all files in the provided folders
    """

    log.info(f"Post populating fmap IntendedFor fields with all files from: {post_populate}")
    sessions = list(dir_sub.glob("ses-*"))
    if not sessions:
        sessions = [dir_sub]

    for sesh in sessions:
        intended_for = []
        # Get dir containing all modalities (could be session or subject)
        dirs = [x for x in sesh.glob("*") if x.is_dir() and "fmap" not in x.name]
        for one_dir in dirs:
            if one_dir.name in post_populate:
                for one_file in one_dir.glob("*.nii*"):
                    log.debug(f"Located {one_file.relative_to(one_dir.parent)}")
                    intended_for.append(one_file.relative_to(one_dir.parent).name)

        if not intended_for:
            log.warning("Filtered IntendedFor field empty")

        intended_for.sort()
        log.debug(intended_for)

        for sidecar in sesh.glob("fmap/*.json"):
            log.debug(f"Editing sidecar: {sidecar}")
            # Read in downloaded sidecar and update the IntendedFor field
            with open(sidecar, "r", encoding="utf-8") as in_json:
                json_decoded = json.load(in_json)

            json_decoded["IntendedFor"] = intended_for

            with open(sidecar, "w", encoding="utf-8") as out_json:
                json.dump(json_decoded, out_json, sort_keys=True, indent=2)


def is_bidsified(scan: "FileEntry", acq: "ContainerAcquisitionOutput") -> bool:
    """
    Check if scan has been properly BIDSified, or if "ignore" field has been checked.

    Args:
        scan: single scan from acquisition container
        acq: acquisition containining scan
    Returns:
        (bool): download file?
    """

    # Check for BIDS information
    try:
        folder_name: str = scan["info"]["BIDS"]["Folder"]
    except (KeyError, TypeError):
        log.debug(f"Not properly BIDSified data: {acq.label}")
        return False

    if folder_name == "":
        log.debug(f"Not properly BIDSified data: {acq.label}")
        try:
            err: str = scan["info"]["BIDS"]["error_message"]
            log.debug(f"BIDS error message: {err}")
            return False
        except (KeyError, TypeError):
            return False

    # Filter out sourcedata (dicoms)
    if folder_name == "sourcedata":
        return False

    # Check for ignore field
    try:
        if scan["info"]["BIDS"]["ignore"] is True:
            log.debug(f"Ignore field True: {acq.label}")
            return False
    except (KeyError, TypeError):
        log.debug(f"No ignore field: {acq.label}")
        return False

    return True


def download_bids_modalities(
    subject: "ContainerSubjectOutput",
    modalities: List[str],
    bids_dir: Path,
    is_dry_run: bool,
    post_populate: Optional[List] = None,
) -> None:
    """
    Download required files by looping through all sessions and acquisitions and analyses to find required files.

    Args:
        subject: flywheel subject object
        modalities: list of modalities to download
        bids_dir: path to bids directory
        dry_run: don't download if True
        post_populate: populate fmap IntendedFor fields will all NIfTI files in the specified modalities
    """

    # Data will not be downloaded if it is a dry run
    if is_dry_run:
        log.info("Dry run: data will not be downloaded")
    else:
        log.info(f"Attempting to download modalities: {modalities}...")

    # Determine if multiple sessions
    num_sessions = len(subject.sessions())

    log.info(f"Found {num_sessions} sessions")

    # Loop through all sessions and acquisitions to find required files
    for session in subject.sessions.iter():
        log.info(f"--- Searching through session:  {session.label} ---")
        for acq in session.reload().acquisitions.iter():
            for scan in acq.reload().files:

                if not is_bidsified(scan, acq):
                    continue

                # Filter out unwanted modalities
                if scan["info"]["BIDS"]["Folder"] not in modalities:
                    continue

                filename: str = scan["info"]["BIDS"]["Filename"]

                log.info(f"Located: {filename}")

                save_path: Path = bids_dir / scan["info"]["BIDS"]["Path"]

                # Only download if not already there and is not dry run
                if not (save_path / filename).is_file() and not is_dry_run:
                    log.info("    downloaded")
                    scan.download(save_path / filename)
                    # Populate the IntendedFor field
                    if "fmap" in str(save_path) and filename.endswith(".json") and not post_populate:
                        populate_intended_for(scan, save_path / filename)

    if post_populate:
        post_populate_intended_for(bids_dir / ("sub-" + subject.label), post_populate)

    log.info("Finished downloading modalities")


def download_bids_files(
    subject: "ContainerSubjectOutput",
    filenames: List[str],
    bids_dir: Path,
    is_dry_run: bool,
) -> None:

    """
    Download required files by looping through all sessions and acquisitions and analyses to find required files.

    Args:
        subject: flywheel subject object
        filenames: list of partial names to use as regex for downloading required files
        bids_dir: path to bids directory
        dry_run: don't download if True
    """

    # Do not download if dry run
    if is_dry_run:
        log.info("Dry run: data will not be downloaded")

    # Determine if multiple sessions
    num_sessions = len(subject.sessions())

    log.info(f"Found {num_sessions} sessions")

    # Loop through all sessions and acquisitions to find required files
    for session in subject.sessions.iter():
        log.info(f"--- Searching through session:  {session.label} ---")
        for acq in session.reload().acquisitions.iter():
            for scan in acq.reload().files:

                if not is_bidsified(scan, acq):
                    continue

                filename: str = scan["info"]["BIDS"]["Filename"]

                # Search through requested files and check for matches
                for name in filenames:
                    if re.search(name, filename):
                        break
                else:
                    continue

                log.info(f"Located: {filename}")

                save_path: Path = bids_dir / scan["info"]["BIDS"]["Path"]

                # Only download if not already there and is not dry run
                if not (save_path / filename).is_file() and not is_dry_run:
                    log.info("    downloaded")
                    scan.download(save_path / filename)
                    # Populate the IntendedFor field
                    if "fmap" in str(save_path) and filename.endswith(".json"):
                        populate_intended_for(scan, save_path / filename)

    log.info("Finished downloading individual files")
