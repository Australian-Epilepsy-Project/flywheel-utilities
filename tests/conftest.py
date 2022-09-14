''' conftest '''

# pylint: disable=import-error
import pytest
from flywheel.models.acquisition import Acquisition
from flywheel.models.file_entry import FileEntry


@pytest.fixture
def acquisition():
    ''' Mock Flywheel acquisition '''

    # Information to fill mock acquisition with
    info = {"label": "2-anat-FLAIR_rec-filtered"}
    return Acquisition(**info)


@pytest.fixture
def field_ignore_scan(request):
    ''' Mock Flywheel scan '''

    filename = "sub-101101_ses-101101_echo-5_part-mag_MEGRE.nii.gz"
    info = {"info": {"BIDS": {"Filename": filename,
                              "Folder": "anat",
                              "Path": "sub-101101/ses-101101/anat",
                              "error_message": "mocked ERROR",
                              "ignore": request.param}}}

    return FileEntry(**info)


@pytest.fixture
def bad_scan():
    ''' Mock Flywheel scan with no BIDS data'''

    info = {"info": ""}

    return FileEntry(**info)
