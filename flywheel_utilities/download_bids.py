'''
Module for downloading bids data from flywheel
'''

import logging
import re
import json

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals


def populate_intended_for(fw_file, sidecar):
    '''
    The json sidecars stored on Flywheel do not have the IntendedFor field populated. Instead, this information is
    found in the metadata. This function is used to populate the field of the downloaded sidecar.

    Args:
        fw_file (flywheel.models.FileEntry): json sidecar file on Flywheel
        sidecar (pathlib.Path): path to saved json sidecar
    '''

    log.debug(f"Populating IntendedFor of: {sidecar}")

    # Retrieve IntendedFor information from metadata
    intended_for_orig = fw_file['info']['IntendedFor']

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
    with open(sidecar, 'r', encoding='utf-8') as in_json:
        json_decoded = json.load(in_json)

    json_decoded['IntendedFor'] = intended_for

    with open(sidecar, 'w', encoding='utf-8') as out_json:
        json.dump(json_decoded, out_json, sort_keys=True, indent=2)


def is_bidsified(scan, acq):
    '''
    Check if scan has been properly BIDSified, or if "ignore" field has been
    checked.

    Args:
        scan (flywheel.models.file_entry.FileEntry): single scan from
        acquisition container
        acq (flywheel.models.acquisition.Acquisition): Flywheel acquisition
        container
    Returns:
        (bool): download file?
    '''

    # Check for BIDS information
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

    # Check for ignore field
    try:
        if scan['info']['BIDS']['ignore'] is True:
            log.debug(f"Ignore field True: {acq.label}")
            return False
    except (KeyError, TypeError):
        log.debug(f"No ignore field: {acq.label}")
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
                    # Populate the IntendedFor field
                    if 'fmap' in str(save_path) and filename.endswith(".json"):
                        populate_intended_for(scan, save_path / filename)

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
                    # Populate the IntendedFor field
                    if 'fmap' in str(save_path) and filename.endswith(".json"):
                        populate_intended_for(scan, save_path / filename)

    log.info("Finished downloading individual files")
