"""
Module for downloading data from flywheel
"""

import logging
import sys
from functools import reduce
from pathlib import Path

# pylint: disable=wrong-import-order
from typing import TYPE_CHECKING, Dict, List
from zipfile import ZipFile

# pylint: disable=import-error
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive  # type: ignore

# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel.models.container_analysis_output import (
        ContainerAnalysisOutput,
    )  # type: ignore
    from flywheel.models.container_subject_output import (
        ContainerSubjectOutput,
    )  # type: ignore
    from flywheel.models.file_entry import FileEntry  # type: ignore

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals


def unzip_result(zip_name: Path, work_dir: Path, is_dry_run: bool) -> int:
    """
    Unzip the downloaded results. Attempts to find the zipped folder name first, however if there are not nested
    folders, the unzip name is determined by stripping the zipped names of everything after and inlcuding "_sub-".
    Only unzips the file if not already present.

    Args:
        zip_name: full path to zip file
        work_dir: path to work directory
        is_dry_run: is this a dry run?
    """

    # Get list of all files in the zip file
    with ZipFile(zip_name, "r") as in_zip:
        dirs = [info.filename for info in in_zip.infolist() if info.is_dir()]
        files = [
            info.filename for info in in_zip.infolist() if not str(info).endswith("/")
        ]

    if len(dirs) == 0 and len(files) == 0:
        log.error("Zip file is empty!")
        return 1

    # Extract the base directory
    if len(dirs) != 0:
        base_dir = Path(dirs[0]).parts[0]
        log.debug(f"Base dir of zipped file: {base_dir}")
    else:
        name = str(zip_name)
        base_dir = Path(name[: name.find("_sub-")]).parts[-1]

    # Check if file already exists
    if not (work_dir / base_dir).exists():
        unzip_archive(zip_name, work_dir, is_dry_run)
    else:
        log.debug("Unzipped file already exists")

    return 0


def download_previous_result(
    subject: "ContainerSubjectOutput",
    results: Dict[str, str],
    work_dir: Path,
    export_gear: bool = False,
    is_dry_run: bool = False,
) -> int:
    """
    Download a result from a specific gear, with the option to filter via the job tags. One can specify if searching for
    processing results or export results via export_gear. Results will be downloaded to 'work_dir'.

    Args:
        subject: flywheel subject object
        results_info: dict containing gear_name, filename and tag.
                    - gear_name: with or without version
                    - filename: used as regex to match output file
                    - tag: used for simple is <tag> in tag search of job tags.
        work_dir: path to work directory
        export_gear: should export runs be included?
        is_dry_run: is this a dry run?
    """

    gear_name = results["gear_name"]
    filename = results["filename"]
    tag = results["tag"]

    log.info(f"Attempting to find previous {gear_name} result")

    analyses = subject.reload().analyses

    # Scan through subject's previous analyses and find all successful runs
    def filter_completed(analysis: "ContainerAnalysisOutput") -> bool:
        if "gear-export" in analysis.job.config["config"]:
            if analysis.job.config["config"]["gear-export"] != export_gear:
                return False
        return (
            gear_name in analysis.gear_info["name"]
            and analysis.job["state"] == "complete"
        )

    analyses = list(filter(filter_completed, analyses))

    # Check we still have analysis ouputs
    if len(analyses) == 0:
        log.error(f"No successful {gear_name} runs were found!")
        return 1

    log.debug(f"Found {len(analyses)} successful gear runs")

    # Filter using tag
    def filter_tag(analysis: "ContainerAnalysisOutput", tag: str) -> bool:
        return bool(tag in analysis.job.tags)

    if tag != "":
        log.debug(f"Using the tag '{tag}' to further filter results")
        analyses = list(filter(lambda filt: filter_tag(filt, tag), analyses))

    # Check we still have analysis ouputs
    if len(analyses) == 0:
        log.error(f"No successful {gear_name} runs survived tag filtering!")
        return 1

    # List potential outputs
    log.debug(f"The following {gear_name} outputs were found:")
    for i in analyses:
        log.debug(f"-version : {i.gear_info['version']}")
        log.debug(f" finished: {i.created}")

    # Select latest output
    def latest_date(
        output1: "ContainerAnalysisOutput", output2: "ContainerAnalysisOutput"
    ) -> "ContainerAnalysisOutput":
        return output1 if output1.created > output2.created else output2

    latest_result = reduce(latest_date, analyses)

    log.info(f"Download results from {latest_result.gear_info['version']}")
    log.info(f"Job id for previous results: {latest_result.id}")

    # Search saved outputs for file and download to work_dir
    for output in latest_result.files:
        log.debug(f"Found: {output.name}")
        if filename in output.name:
            log.info(f"Found: {output.name}")
            download_name = work_dir / output.name
            if not download_name.is_file():
                log.info(f"Downloading: {download_name.name}")
                output.download(download_name)
                break

    # Check file was downloaded
    try:
        download_name.is_file()
    except UnboundLocalError:
        log.error("Could not locate requested file.")
        return 1

    log.info("Successfully downloaded")

    if str(download_name).endswith(".zip"):
        return unzip_result(download_name, work_dir, is_dry_run)

    return 0


def download_specific_result(
    analysis: "ContainerAnalysisOutput", filename: str, work_dir: Path, is_dry_run: bool
) -> None:
    """
    Download results using destination ID from previous gear run. Results will be downloaded into work_dir.

    Args:
        analysis:
        filename: string used to find output file (substring matching)
        work_dir: path to work directory
        is_dry_run: is this a dry run?
    """

    log.info("Scanning analysis output files for an output " f"containing '{filename}'")

    files: List["FileEntry"] = analysis.files

    if len(files) == 0:
        log.error("Analysis has no output files")
        sys.exit(1)

    for output in files:
        log.debug(f"Found: {output.name}")
        if filename in output.name:
            log.info(f"Found: {output.name}")
            download_name = work_dir / output.name
            if not download_name.is_file():
                log.info(f"Downloading: {download_name.name}")
                output.download(download_name)
            else:
                log.debug("Zip file already exists. Must be testing")
            break

    # Check file was downloaded
    try:
        Path(download_name).is_file()
    except UnboundLocalError:
        log.error("Could not locate file")
        sys.exit(1)

    log.info("Successfully downloaded")

    if str(download_name).endswith(".zip"):
        unzip_result(download_name, work_dir, is_dry_run)
