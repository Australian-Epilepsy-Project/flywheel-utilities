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
    Check if scan has been properly BIDSified, or if "ignore" field has been
    checked.

    Args:
        scan (flywheel.models.file_entry.FileEntry): single scan from
        acquisition container
        acq (flywheel.models.container_session_output.ContainerSessionOutput)
    Returns:
        (bool): download file?
    '''

    # Filter out dicoms
    if scan.type.lower() == 'dicom':
        return False
    # Check has BIDS information
    try:
        _dummy = scan.info['BIDS']
    except (KeyError, TypeError):
        log.debug(f"Not properly BIDSified data: {acq.label}")
        return False

    # Check ignore and valid fields exist
    if not all(key in scan.info['BIDS'] for key in ['ignore', 'valid']):
        log.debug(f"File missing ignore or valid field: {acq.label}")
        return False

    if scan.info['BIDS']['ignore'] is True:
        log.debug(f"Ignore field True: {acq.label}")
        return False
     
    if scan.info['BIDS']['valid'] is False:
        log.debug(f"Valid field False: {acq.label}")
        return False

    return True


def save_file(scan, bids_dir, is_dry_run):
    '''
    Save selected NIfTI file to BIDS directory

    Args:
        scan (flywheel.models.file_entry.FileEntry): file to download
        bids_dir (pathlib.Path): path to BIDS directory
        is_dry_run (bool): is dry run?
    '''
    filename = scan.info['BIDS']['Filename']

    log.info(f"Located: {filename}")

    save_path = bids_dir / scan.info['BIDS']['Path']

    # Only download if not already there and is not dry run
    if not (save_path / filename).is_file() and not is_dry_run:
        log.info("    downloaded")
        scan.download(save_path / filename)


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

    if is_dry_run:
        log.info("Dry run: data will not be downloaded")
    else:
        log.info(f"Attempting to download modalities: {modalities}...")

    log.info(f"Subject has {len(subject.sessions())} sessions")

    # Loop through all sessions and acquisitions to find required files
    for session in subject.sessions.iter():
        log.info(f"--- Searching through session:  {session.label} ---")
        for acq in session.reload().acquisitions.iter():

            if acq['info_exists'] == False:
                continue 

            for scan in acq.reload().files:

                if not is_bidsified(scan, acq):
                    continue

                # Filter out unwanted modalities
                if scan.info['BIDS']['Folder'] not in modalities:
                    continue

                save_file(scan)
               
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

    if is_dry_run:
        log.info("Dry run: data will not be downloaded")
    else:
        log.info(f"Attempting to download files: {filenames}...")

    log.info(f"Subject has {len(subject.sessions())} sessions")

    # Loop through all sessions and acquisitions to find required files
    for session in subject.sessions.iter():
        log.info(f"--- Searching through session:  {session.label} ---")
        for acq in session.reload().acquisitions.iter():
            
            if acq['info_exists'] == False:
                continue 

            for scan in acq.reload().files:

                if not is_bidsified(scan, acq):
                    continue

                filename = scan.info['BIDS']['Filename']

                # Search through requested files and check for matches
                for name in filenames:
                    if re.search(name, filename):
                        break
                else:
                    continue

                save_file(scan)

    log.info("Finished downloading individual files")
