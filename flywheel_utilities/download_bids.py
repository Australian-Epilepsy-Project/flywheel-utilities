'''
Module for downloading bids data from flywheel
'''

import logging
import re

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals


def is_bidsified(scan, acq):
    '''
    Check if scan has been properly BIDSified.

    Args:
        scan (flywheel.models.file_entry.FileEntry): single scan from
        acquisition container
        acq (flywheel.models.acquisition.Acquisition): Flywheel acquisition
        container
    Returns:
        (bool): BIDSified?
    '''

    try:
        _is_bids = scan['info']['BIDS']
    except (KeyError, TypeError):
        return False

    try:
        folder_name = scan['info']['BIDS']['Folder']
    except (KeyError, TypeError):
        log.debug(f"Not properly BIDSified data: {acq.label}")
        return False

    if folder_name == "":
        log.debug(f"Not properly BIDSified data: {acq.label}")
        try:
            err = scan['info']['BIDS']['error_message']
            log.debug(f"BIDS error message: {err}")
            return False
        except (KeyError, TypeError):
            return False

    # Filter out sourcedata (dicoms)
    if folder_name == 'sourcedata':
        return False

    return True


def download_bids_modalities(subject,
                             modalities,
                             bids_dir,
                             is_dry_run):
    '''
    Download required files by looping through all sessions and acquisitions
    and analyses to find required files.

    Args:
        subject (flywheel.models.Subject): flywheel subject object
        modalities (list(str)): list of modalities to download
        bids_dir (pathlib.Path): path to bids directory
        dry_run (bool): don't download if True
    '''

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
                if scan['info']['BIDS']['Folder'] not in modalities:
                    continue

                filename = scan['info']['BIDS']['Filename']

                log.info(f"Located: {filename}")

                save_path = bids_dir / scan['info']['BIDS']['Path']

                # Only download if not already there and is not dry run
                if not (save_path / filename).is_file() and not is_dry_run:
                    log.info("    downloaded")
                    scan.download(save_path / filename)

    log.info("Finished downloading modalities")


def download_bids_files(subject,
                        filenames,
                        bids_dir,
                        is_dry_run):

    '''
    Download required files by looping through all sessions and acquisitions
    and analyses to find required files.

    Args:
        subject (flywheel.models.Subject): flywheel subject object
        filenames (list(str)): list of partial names to use as regex for
                                downloading required files
        bids_dir (pathlib.Path): path to bids directory
        dry_run (bool): don't download if True
    '''

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

                filename = scan['info']['BIDS']['Filename']

                # Search through requested files and check for matches
                for name in filenames:
                    if re.search(name, filename):
                        break
                else:
                    continue

                log.info(f"Located: {filename}")

                save_path = bids_dir / scan['info']['BIDS']['Path']

                # Only download if not already there and is not dry run
                if not (save_path / filename).is_file() and not is_dry_run:
                    log.info("    downloaded")
                    scan.download(save_path / filename)

    log.info("Finished downloading individual files")
