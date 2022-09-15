''' conftest '''

# pylint: disable=import-error
import pytest
from flywheel.models.file_entry import FileEntry
from flywheel.models.acquisition import Acquisition


@pytest.fixture
def acquisition():
    ''' Mock Flywheel acquisition '''

    # Information to fill mock acquisition with
    info = {"label": "2-anat-FLAIR_rec-filtered"}
    return Acquisition(**info)


@pytest.fixture
def test_scan(request):
    ''' Mock Flywheel scan '''

    filename = "sub-101101_ses-101101_echo-5_part-mag_MEGRE.nii.gz"
    info = {"info": {"BIDS": {"Filename": filename,
                              "Folder": "anat",
                              "Path": "sub-101101/ses-101101/anat",
                              "error_message": "mocked ERROR",
                              "ignore": request.param['ignore'],
                              "valid": request.param['valid']}},
            "type": request.param['type']}


    return FileEntry(**info)


@pytest.fixture
def bad_scan():
    ''' Mock Flywheel scan with no BIDS data'''

    info = {"info": ""}

    return FileEntry(**info)
