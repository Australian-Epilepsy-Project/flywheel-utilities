'''
Tests for download_bids.py
'''


# pylint: disable=import-error
import logging
from pathlib import Path
from unittest.mock import MagicMock
from flywheel.models.subject import Subject
import pytest
from flywheel_utilities import download_bids
from tests.mock_classes import mock_scan


def test_dont_ignore_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified with ignore = False '''

    test_scan = mock_scan("T1w.nii", "anat", "sub-1/anat", False, True, "nifti")

    with caplog.at_level(logging.INFO):
        download = download_bids.is_bidsified(test_scan, acquisition)
    assert download is True
    assert len(caplog.messages) == 0


def test_ignore_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified with ignore = True '''

    test_scan = mock_scan("T1w.nii", "anat", "sub-1/anat", True, True, "nifti")

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(test_scan, acquisition)

    assert download is False
    assert caplog.messages[0] == f"Ignore field True: {acquisition.label}"


def test_not_valid_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified with ignore = True '''

    test_scan = mock_scan("T1w.nii", "anat", "sub-1/anat", False, False, "nifti")

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(test_scan, acquisition)

    assert download is False
    assert caplog.messages[0] == f"Valid field False: {acquisition.label}"


def test_bad_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified when scan missing BIDS info'''

    bad_scan = mock_scan("T1w.nii", "anat", "sub-1/anat", True, False, "nifti")

    # Remove BIDS info
    del bad_scan.info['BIDS']

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(bad_scan, acquisition)
    
    assert download is False
    assert caplog.messages[0] == f"Not properly BIDSified data: {acquisition.label}"


def test_missing_valid_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified when scan missing BIDS info'''

    bad_scan = mock_scan("T1w.nii", "anat", "sub-1/anat", True, False, "nifti")

    # Remove BIDS info
    del bad_scan.info['BIDS']['valid']

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(bad_scan, acquisition)
    
    assert download is False
    assert caplog.messages[0] == f"File missing ignore or valid field: {acquisition.label}"


def test_dry_save_file(tmp_path, caplog):
    ''' Test dry run saving file '''

    scan = mock_scan("T1w.nii.gz", "anat", "sub-1/anat", False, True, "nifti")

    with caplog.at_level(logging.INFO):
        download_bids.save_file(scan, Path(tmp_path), True)

    assert caplog.messages[0] == "Located: T1w.nii.gz"


def test_dry_save_file(caplog):
    ''' Test dry run saving file '''

    scan = mock_scan("T1w.nii.gz", "anat", "sub-1/anat", False, True, "nifti")

    with caplog.at_level(logging.INFO):
        download_bids.save_file(scan, Path("./"), True)

    assert caplog.messages[0] == "Located: T1w.nii.gz"

def test_missing_BIDS_save_file(caplog):
    ''' Test dry run saving file. Should never happen...'''

    bad_scan = mock_scan("T1w.nii.gz", "anat", "sub-1/anat", False, True, "nifti")

    # Remove BIDS info
    del bad_scan.info['BIDS']

    with pytest.raises(KeyError) as error:
        download_bids.save_file(bad_scan, Path("./"), True)

    assert str(error.value) == "'BIDS'"


