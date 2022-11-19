
'''
Test for download_bids.py
'''

import logging
import json
from collections import namedtuple
from pathlib import Path

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

def test_is_bidsified_success(caplog):
    ''' Test successful check '''

    # Mock scan
    mock_scan = {'info': {'BIDS': {'Folder': 'anat',
                                   'ignore': False}
                                   }}

    with caplog.at_level(logging.DEBUG):
        ret = download_bids.is_bidsified(mock_scan, "dummy_var")

    assert ret is True


def test_is_bidsified_missing_folder(caplog):
    ''' Test missing folder name '''

    # Mock scan
    mock_scan = {'info': {'BIDS': {'Folder': '',
                                   'ignore': False}
                                   }}

    Acq = namedtuple('acq', 'label')

    acq = Acq('mock_label')

    with caplog.at_level(logging.DEBUG):
        ret = download_bids.is_bidsified(mock_scan, acq)

    assert ret is False
    assert caplog.messages[0] == 'Not properly BIDSified data: mock_label'


def test_is_bidsified_sourcedata(caplog):
    ''' Test data is sourcedata '''

    # Mock scan
    mock_scan = {'info': {'BIDS': {'Folder': 'sourcedata',
                                   'ignore': False}
                                   }}

    Acq = namedtuple('acq', 'label')

    acq = Acq('mock_label')

    with caplog.at_level(logging.DEBUG):
        ret = download_bids.is_bidsified(mock_scan, acq)

    assert ret is False
    assert len(caplog.messages) == 0


def test_is_bidsified_ignore(caplog):
    ''' Test ignore field is True '''

    # Mock scan
    mock_scan = {'info': {'BIDS': {'Folder': 'anat',
                                   'ignore': True}
                                   }}

    Acq = namedtuple('acq', 'label')

    acq = Acq('mock_label')

    with caplog.at_level(logging.DEBUG):
        ret = download_bids.is_bidsified(mock_scan, acq)

    assert ret is False
    assert caplog.messages[0] == 'Ignore field True: mock_label'


def test_is_bidsified_ignore_missing(caplog):
    ''' Test ignore field missing '''

    # Mock scan
    mock_scan = {'info': {'BIDS': {'Folder': 'anat' }}}

    Acq = namedtuple('acq', 'label')

    acq = Acq('mock_label')

    with caplog.at_level(logging.DEBUG):
        ret = download_bids.is_bidsified(mock_scan, acq)

    assert ret is False
    assert caplog.messages[0] == 'No ignore field: mock_label'
