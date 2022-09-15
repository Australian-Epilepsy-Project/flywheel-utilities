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
