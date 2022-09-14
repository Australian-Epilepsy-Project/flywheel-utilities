'''
Tests for download_bids.py
'''

import logging

# pylint: disable=import-error
import pytest
from flywheel_utilities import download_bids

logger = logging.getLogger()


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
