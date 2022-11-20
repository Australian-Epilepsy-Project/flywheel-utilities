
'''
Test for download_bids.py
'''

import logging
import json
from pathlib import Path
# pylint: disable=import-error
import pytest

from tests.mock_classes import MockScan

from flywheel_utilities import download_bids

def test_intendedfor_pass(tmp_path, caplog):
    ''' Test successful population of IntendedFor '''

    # Mock flyhweel FileEntry
    mock_fw_file = {'info': {'IntendedFor': ['/func/sub-101101_task-rest.nii.gz',
                                             '/func/sub-101101_task-oneback.nii.gz']
                            }
                    }

    # Mock sidecar
    sidecar = Path(tmp_path) / "mock_sidecar.json"

    mock_side_contents = {"AcquisitionMatrixPE": 112,
                          "AcquisitionNumber": 1,

                          "InstitutionName": "Melbourne Brain Centre",
                          "InstitutionalDepartmentName": "Department",
                          "IntendedFor": []
    }

    # Write to file
    with open(sidecar, 'w', encoding='utf-8') as in_json:
        json.dump(mock_side_contents, in_json)

    # Pass to function
    with caplog.at_level(logging.DEBUG):
        download_bids.populate_intended_for(mock_fw_file, sidecar)

    # Check if written file contains new list
    with open(sidecar, 'r', encoding='utf-8') as out_json:
        contents = json.load(out_json)
        assert len(contents['IntendedFor']) == 2


    assert caplog.messages[0] == f'Populating IntendedFor of: {sidecar}'


def test_intendedfor_fail(tmp_path, caplog):
    ''' Test unsuccessful population of IntendedFor '''

    # Mock flyhweel FileEntry containing only json files in IntendedFor field
    mock_fw_file = {'info': {'IntendedFor': ['/func/sub-101101_task-rest.json',
                                             '/func/sub-101101_task-oneback.json']
                            }}

    # Mock sidecar
    sidecar = Path(tmp_path) / "mock_sidecar.json"

    mock_side_contents = {"AcquisitionMatrixPE": 112,
                            "AcquisitionNumber": 1,

                            "InstitutionName": "Melbourne Brain Centre",
                            "InstitutionalDepartmentName": "Department",
                            "IntendedFor": []
    }

    # Write to file
    with open(sidecar, 'w', encoding='utf-8') as in_json:
        json.dump(mock_side_contents, in_json)

    # Pass to function
    with caplog.at_level(logging.DEBUG):
        download_bids.populate_intended_for(mock_fw_file, sidecar)

    # Check if written file contains new list
    with open(sidecar, 'r', encoding='utf-8') as out_json:
        contents = json.load(out_json)
        assert len(contents['IntendedFor']) == 0


    assert caplog.messages[0] == f'Populating IntendedFor of: {sidecar}'
    assert caplog.messages[1] == 'Filtered IntendedFor field empty'

def test_dont_ignore_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified with ignore = False '''

    test_scan = MockScan("T1w.nii", "anat", "sub-1/anat", False, True, "nifti")

    with caplog.at_level(logging.INFO):
        download = download_bids.is_bidsified(test_scan, acquisition)
    assert download is True
    assert len(caplog.messages) == 0


def test_ignore_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified with ignore = True '''

    test_scan = MockScan("T1w.nii", "anat", "sub-1/anat", True, True, "nifti")

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(test_scan, acquisition)

    assert download is False
    assert caplog.messages[0] == f"Ignore field True: {acquisition.label}"


def test_not_valid_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified with ignore = True '''

    test_scan = MockScan("T1w.nii", "anat", "sub-1/anat", False, False, "nifti")

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(test_scan, acquisition)

    assert download is False
    assert caplog.messages[0] == f"Valid field False: {acquisition.label}"


def test_bad_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified when scan missing BIDS info'''

    bad_scan = MockScan("T1w.nii", "anat", "sub-1/anat", True, False, "nifti")

    # Remove BIDS info
    del bad_scan.info['BIDS']

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(bad_scan, acquisition)

    assert download is False
    assert caplog.messages[0] == f"Not properly BIDSified data: {acquisition.label}"


def test_missing_valid_scan_is_bidsified(acquisition, caplog):
    ''' Test is_bidsified when scan missing BIDS info'''

    bad_scan = MockScan("T1w.nii", "anat", "sub-1/anat", True, False, "nifti")

    # Remove BIDS info
    del bad_scan.info['BIDS']['valid']

    with caplog.at_level(logging.DEBUG):
        download = download_bids.is_bidsified(bad_scan, acquisition)

    assert download is False
    assert caplog.messages[0] == f"File missing ignore or valid field: {acquisition.label}"


def test_dry_save_file(caplog):
    ''' Test dry run saving file '''

    scan = MockScan("T1w.nii.gz", "anat", "sub-1/anat", False, True, "nifti")

    with caplog.at_level(logging.INFO):
        download_bids.save_file(scan, Path("./"), True)

    assert caplog.messages[0] == "Located: T1w.nii.gz"


def test_missing_bids_save_file():
    ''' Test dry run saving file. Should never happen...'''

    bad_scan = MockScan("T1w.nii.gz", "anat", "sub-1/anat", False, True, "nifti")

    # Remove BIDS info
    del bad_scan.info['BIDS']

    with pytest.raises(KeyError) as error:
        download_bids.save_file(bad_scan, Path("./"), True)

    assert str(error.value) == "'BIDS'"
