'''
Tests for download_bids.py
'''

import logging

# pylint: disable=import-error
from unittest.mock import MagicMock
from flywheel.models.subject import Subject
import pytest

from flywheel_utilities import download_bids



@pytest.mark.parametrize('field_ignore_scan', [False], indirect=True)
def test_dont_ignore_scan_is_bidsified(acquisition, field_ignore_scan):
    ''' Test is_bidsified with ignore = False '''

    assert download_bids.is_bidsified(field_ignore_scan, acquisition) is True


@pytest.mark.parametrize('field_ignore_scan', [True], indirect=True)
def test_do_ignore_scan_is_bidsified(acquisition, field_ignore_scan):
    ''' Test is_bidsified with ignore = True '''

    assert download_bids.is_bidsified(field_ignore_scan, acquisition) is False


def test_bad_scan_is_bidsified(acquisition, bad_scan):
    ''' Test is_bidsified when scan missing BIDS info'''

    assert download_bids.is_bidsified(bad_scan, acquisition) is False

# Dry run
def test_dry_run_download_bids_modalities(tmp_path, caplog):
    ''' Test download_bids with good file '''

    subject = Subject()

    subject.sessions = MagicMock(return_value=[1, 2])

    with caplog.at_level(logging.INFO):
        download_bids.download_bids_modalities(subject, ['anat'], tmp_path, True)

    # Logs when primary loop is skipped
    logs = ['Dry run: data will not be downloaded',
            'Found 2 sessions',
            'Finished downloading modalities']

    assert caplog.messages == logs
