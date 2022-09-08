'''
Module for downloading data from flywheel
'''

import logging
import sys
from pathlib import Path
from functools import reduce
from zipfile import ZipFile
# pylint: disable=import-error
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive
# pylint: enable=import-error

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals


def unzip_result(zip_name, work_dir, is_dry_run):
    '''
    Unzip the downloaded results. Only unzips the file if not already present.

    Args:
        zip_name (pathlib.Path): full path to zip file
        work_dir (pathlib.Path): path to work directory
        is_dry_run (bool): is this a dry run?
    '''

    # Get list of all directories in the zip file
    with ZipFile(zip_name, 'r') as in_zip:
        dirs = [info.filename for info in in_zip.infolist() if info.is_dir()]

    if len(dirs) == 0:
        log.error("Zip file is empty!")
        return 1

    # Extract the base directory
    base_dir = Path(dirs[0]).parts[0]
    log.debug(f"Base dir of zipped file: {base_dir}")

    # Check if file already exists
    if not (work_dir / base_dir).exists():
        unzip_archive(zip_name, work_dir, is_dry_run)
    else:
        log.debug("Unzipped file already exists")

    return 0


def download_previous_result(subject,
                             results,
                             work_dir,
                             export_gear=False,
                             is_dry_run=False):
    '''
    Download a result from a specific gear, with the option to filter via the
    job tags. One can specify if searching for processing results or export
    results via export_gear. Results will be downloaded to 'work_dir'.

    Args:
        subject (flywheel.models.Subject): flywheel subject object
        results_info (dict): dict containing gear_name, filename and tag.
                    - gear_name: with or without version
                    - filename: used as regex to match output file
                    - tag: used for simple is <tag> in tag search of job tags.
        work_dir (pathlib.Path): path to work directory
        export_gear (bool): should export runs be included?
        is_dry_run (bool): is this a dry run?
    '''

    gear_name = results['gear_name']
    filename = results['filename']
    tag = results['tag']

    log.info(f"Attempting to find previous {gear_name} result")

    analyses = subject.reload().analyses

    # Scan through subject's previous analyses and find all successful runs
    def filter_completed(analysis):
        if 'gear-export' in analysis.job.config['config']:
            if analysis.job.config['config']['gear-export'] != export_gear:
                return False
        return gear_name in analysis.gear_info['name'] and \
               analysis.job['state'] == 'complete'

    analyses = list(filter(filter_completed, analyses))

    # Check we still have analysis ouputs
    if len(analyses) == 0:
        log.error(f"No successful {gear_name} runs were found!")
        return 1

    log.debug(f"Found {len(analyses)} successful gear runs")

    # Filter using tag
    def filter_tag(analyses, tag):
        return bool(tag in analyses.job.tags)

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
    def latest_date(output1, output2):
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


def download_specific_result(analysis, filename, work_dir, is_dry_run):
    '''
    Download results using destination ID from previous gear run. Results will
    be downloaded into work_dir.

    Args:
        analysis (flywheel.models.analysis_output.AnalysisOutput)
        filename (str): string used to find output file (substring matching)
        work_dir (pathlib.Path): path to work directory
        is_dry_run (bool): is this a dry run?
    '''

    log.info("Scanning analysis output files for an output "
             f"containing '{filename}'")

    files = analysis.files

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
