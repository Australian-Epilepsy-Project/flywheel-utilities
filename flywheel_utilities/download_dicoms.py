"""
Module for downloading data from flywheel
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, List

from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

from flywheel_utilities import download_bids

# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel.models.container_subject_output import ContainerSubjectOutput


log = logging.getLogger(__name__)


def dicom_unzip_name(name: str) -> str:
    """
    Construct name for unzipped DICOM series from label on Flywheel. Remove spaces and .zip.

    Args:
        name: filename
    Returns:
        clean_name: filename
    """

    clean_name = name.replace(".dicom", "")
    clean_name = clean_name.replace(".zip", "")
    clean_name = clean_name.replace(" ", "_")
    return clean_name.replace("_-_", "-")


# pylint: disable=too-many-branches
def download_specific_dicoms(
    subject: "ContainerSubjectOutput",
    filenames: List[str],
    work_dir: Path,
    is_dry_run: bool = False,
) -> List[Path]:
    """
    Download a zipped DICOM series. Use the BIDsified file names for the NIfTI files to find the container containing
    the correct DICOM series.

    Args:
        subject: flywheel subject object
        filenames: list of BIDsified file names
        work_dir: path to working directory
        is_dry_run: download results?
    Returns:
        orig_dicoms: path to unzipped DICOMs
    """

    log.info("--------------------------------------------")
    log.info("Downloading specific DICOM series")

    # Track number of downloads
    num_files = len(filenames)
    num_downloads = 0

    orig_dicoms: List[Path] = []

    for session in subject.sessions.iter():
        for acq in session.reload().acquisitions.iter():
            # Loop over files, search for the NIfTIs that were used in the
            # analysis, then download the DICOMs found in the same container
            download = False
            for scan in acq.reload().files:

                if not download_bids.is_bidsified(scan, acq):
                    continue

                filename: str = scan["info"]["BIDS"]["Filename"]

                # Search through requested files and check for matches
                for name in filenames:
                    if re.search(name, filename):
                        download = True
                        break
                else:
                    continue

                log.info(f"Located: {filename}")

                if download is True:
                    break

            # If the correct BIDs file was found, reloop over the scans and
            # download the DICOM series
            if download is not True:
                continue

            for scan in acq.files:
                if scan.type.lower() == "dicom":
                    series_name = Path(scan.name)
                    if not (work_dir / series_name).is_file():
                        scan.download(work_dir / series_name)
                    num_downloads += 1
                    break

            # Unzip the file
            unzip_name: Path = work_dir / dicom_unzip_name(str(series_name))
            if not series_name.is_dir():
                unzip_archive(work_dir / series_name, unzip_name, is_dry_run)

            orig_dicoms.append(unzip_name)

            # Return early if requested DICOMs have already been found
            if num_downloads == num_files:
                return orig_dicoms

    # If completed looping over all sessions, check the correct number of DICOM
    # series were downloaded
    if num_downloads != num_files:
        log.warning("Could not find all the requested DICOM series")
        log.warning(f"Only {num_downloads}/{num_files} downloaded")
        log.warning(f"Provided strings: {filenames}")

    return orig_dicoms


def download_all_dicoms(
    subject: "ContainerSubjectOutput",
    work_dir: Path,
    to_ignore: List[str],
    dicom_dir: Path,
    is_dry_run: bool,
) -> None:
    """
    Download all DICOM series for a subject with the option to filter using to_ignore.

    Args:
        subject: flywheel subject object
        work_dir: path to working directory for download
        to_ignore: list of strings used to reject DICOMS for download
        dicom_dir: directory to extract DICOM series to
        is_dry_run: download results?
    """

    log.info("--------------------------------------------")
    log.info("Downloading multiple DICOM series")

    # Track number of downloads
    for session in subject.sessions.iter():
        for acq in session.reload().acquisitions.iter():
            # Loop over files, search for the NIfTIs that were used in the
            # analysis, then download the DICOMs housed in the same contained
            for scan in acq.reload().files:

                # Only interested in DICOMS
                if not scan.type.lower() == "dicom":
                    continue

                # Filter DICOMS
                to_download = True
                for ignore in to_ignore:
                    if ignore.lower() in scan.name.lower():
                        log.debug(f"Will not download: {scan.name}")
                        to_download = False

                if to_download is False:
                    continue

                log.info(f"Found: {scan.name}")
                download_name: Path = work_dir / scan.name

                if not download_name.exists():
                    log.debug("   downloading...")
                    scan.download(download_name)

                unzip_name: str = dicom_unzip_name(scan.name)

                # Unzip the file
                unzip_dir = dicom_dir / unzip_name
                if not unzip_dir.exists():
                    unzip_archive(download_name, unzip_dir, is_dry_run)
