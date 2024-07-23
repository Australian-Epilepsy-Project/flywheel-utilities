"""
Module for downloading data from flywheel
"""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, List

from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

from flywheel_utilities import download_bids

if TYPE_CHECKING:
    from flywheel.models.container_subject_output import ContainerSubjectOutput


log = logging.getLogger(__name__)


def dicom_unzip_name(name: str) -> str:
    """
    Construct name for unzipped DICOM series from label on Flywheel. Remove spaces and .zip.

    Parameters
    ----------
    name:
        filename

    Returns
    -------
        clean file name
    """

    clean_name: str = name.replace(".dicom", "")
    clean_name = clean_name.replace(".zip", "")
    clean_name = clean_name.replace(" ", "_")
    return clean_name.replace("_-_", "-")


# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-statements
def download_specific_dicoms(
    subject: ContainerSubjectOutput,
    filenames: List[str],
    work_dir: Path,
    is_dry_run: bool = False,
) -> List[Path]:
    """
    Download a zipped DICOM series. Use the BIDsified file names from the NIfTI file(s) to find the
    container housing the DICOM series, then use SeriesNumber to find the correct DICOM in the
    Flywheel container.

    Parameters
    ----------
    subject:
        Flywheel subject object
    filenames:
        list of BIDsified file names
    work_dir:
        Path to working directory
    is_dry_run:
        download results?

    Returns
    -------
        list of Paths to unzipped DICOMs
    """

    log.info("--------------------------------------------")
    log.info("Downloading specific DICOM series")

    # Track number of downloads
    num_files: int = len(filenames)
    num_downloads: int = 0

    orig_dicoms: List[Path] = []

    for session in subject.sessions.iter():
        for acq in session.reload().acquisitions.iter():
            # Check if ignore is set at acquisition level
            if "BIDS" in acq.info:
                if acq.info["BIDS"]["ignore"] is True:
                    continue

            # Loop over files, search for the NIfTIs that were used in the
            # analysis, then download the DICOMs found in the same container
            download: bool = False
            for scan in acq.reload().files:
                if not download_bids.is_bidsified(scan, acq):
                    continue

                filename: str = scan["info"]["BIDS"]["Filename"]

                # Search through requested files and check for matches
                for name in filenames:
                    if re.search(name, filename):
                        download = True
                        # Extract series number to use as unique identifier
                        try:
                            series_number = scan.info["header"]["dicom"]["SeriesNumber"]
                        except KeyError:
                            series_number = scan.info["SeriesNumber"]
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

            for scan in acq.reload().files:
                if scan.type.lower() == "dicom":
                    # Extract scan information which will be used to match with correct DICOM
                    try:
                        series_number_dicom = scan.info["header"]["dicom"]["SeriesNumber"]
                    except KeyError:
                        series_number_dicom = scan.info["SeriesNumber"]

                    if series_number_dicom == series_number:
                        is_zipped: bool = scan.name.lower().endswith(".zip")
                        scan_name: str = scan.name.replace(" ", "_")
                        if not is_zipped:
                            download_dir_enhanced = work_dir / scan_name.partition(".")[0]
                            log.debug(f"  creating: {download_dir_enhanced}")
                            download_dir_enhanced.mkdir(exist_ok=True)
                            download_name = download_dir_enhanced / scan_name
                        else:
                            download_name = work_dir / scan_name
                        if not download_name.is_file():
                            scan.download(download_name)
                        num_downloads += 1
                        break

            log.debug(f"  {download_name=}")
            # If dealing with classic DICOMS, unzip the file
            if is_zipped:
                unzip_name: Path = work_dir / dicom_unzip_name(scan_name)
                if not download_name.is_dir() and is_dry_run is False:
                    unzip_archive(download_name, unzip_name, is_dry_run)
                log.debug(f" -> {unzip_name}")

                orig_dicoms.append(unzip_name)
            else:
                orig_dicoms.append(download_dir_enhanced)

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
    subject: ContainerSubjectOutput,
    work_dir: Path,
    to_ignore: List[str],
    dicom_dir: Path,
    is_dry_run: bool,
) -> None:
    """
    Download all DICOM series for a subject with the option to filter using to_ignore.

    Parameters
    ----------
    subject:
        Flywheel subject object
    work_dir:
        Path to working directory for download
    to_ignore:
        list of strings used to reject DICOMS for download
    dicom_dir:
        directory to extract DICOM series to
    is_dry_run:
        download results?
    """

    log.info("--------------------------------------------")
    log.info("Downloading multiple DICOM series")

    # Track number of downloads
    for session in subject.sessions.iter():
        for acq in session.reload().acquisitions.iter():
            # Filter
            skip_container: bool = False
            for ignore in to_ignore:
                if ignore.lower() in acq.label.lower():
                    log.debug(f"Will not download: {acq.label}")
                    skip_container = True
            if skip_container:
                continue

            # Check if ignore is set at acquisition level
            if "BIDS" in acq.info:
                if acq.info["BIDS"]["ignore"] is True:
                    continue

            for scan in acq.reload().files:
                # Only interested in DICOMS
                if not scan.type.lower() == "dicom":
                    continue

                log.info(f"Found: {scan.name}")

                is_zipped: bool = scan.name.lower().endswith(".zip")

                scan_name: str = scan.name.replace(" ", "_")
                download_name: Path = work_dir / scan_name

                log.debug(f"  {download_name=}")

                if not download_name.exists():
                    log.debug("   downloading...")
                    scan.download(download_name)

                # Unzip the file
                unzip_name: Path = dicom_dir / dicom_unzip_name(scan_name)
                log.debug(f"  {unzip_name=}")
                if is_zipped:
                    if not unzip_name.exists() and is_dry_run is False:
                        unzip_archive(download_name, unzip_name, is_dry_run)
                else:
                    log.info(f"   moving to: {unzip_name}")
                    unzip_name.mkdir(exist_ok=True)
                    shutil.move(str(download_name), unzip_name / scan_name)
                log.debug(f" -> {unzip_name}")
