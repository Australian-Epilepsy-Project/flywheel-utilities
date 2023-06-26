"""
Simple mocks of Flywheel classes
"""

from pathlib import Path

import flywheel


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# Mock context manager
class Context:
    """Dummy class docstring"""

    def __init__(
        self,
        debug_level="INFO",
        working_dir="",
        gear_name="dummy-name",
        gear_version="3.14.2_0.11.0",
        fs_licence=True,
    ):
        self.config = {"gear-log-level": debug_level}
        self.work_dir = Path(working_dir)
        self.manifest = {"label": gear_name, "version": gear_version}
        self.destination = {"id": "tests"}
        self.fs_licence = fs_licence
        self.client = Client(self.fs_licence)


class Client:
    def __init__(self, fs_license: bool = True):
        self.fs_license = fs_license

    def get_analysis(self, _i):
        dummy_dict = {"parents": {"project": "unit_tests"}}
        return dummy_dict

    def get_project(self, _j):
        if self.fs_license:
            return {"info": {"FREESURFER_LICENSE": "insert_license"}}

        return {"info": {}}

    def add_subject_tag(self, sub_id, gear_name):  # pylint: disable=unused-argument
        return None

    def get(self):
        pass


class MockSubject:
    def __init__(self, has_tags=True, state_scans="valid"):
        if has_tags:
            self.tags = ["megre2swi:1.1.1", "dwi2adc"]
        else:
            self.tags = []
        self.id = "1234567890"  # pylint: disable=invalid-name
        self.label = "sub-101101"
        self._sessions = [MockSession(1, state_scans)]

    def sessions(self):
        return self._sessions


class MockSession:
    def __init__(self, num_sess, state_scans):
        self.label = f"ses-{num_sess}"
        self._acquisitions = [MockAcq(1, state_scans)]

    def acquisitions(self):
        return self._acquisitions

    def reload(self):
        return self


class MockAcq:
    def __init__(self, label, state=0):
        self.label = f"{label}"

        self.files = [MockScan(state)]  # , MockScan(state="valid", is_dicom=True)]

        print(self.files)

    def reload(self):
        return self


class MockScan:
    def __init__(
        self,
        state="valid",
        foldername="anat",
        ignore=False,
        is_dicom=False,
        err_message="",
        ignore_missing=False,
    ):
        self.info = {"BIDS": {}}
        if state == "valid":
            self.info["BIDS"]["Filename"] = "file1"
            if ignore_missing is False:
                self.info["BIDS"]["ignore"] = ignore
            self.info["BIDS"]["Path"] = "sub-101101/ses-01/anat"
            if foldername is not None:
                self.info["BIDS"]["Folder"] = foldername
            if err_message is not None:
                self.info["BIDS"]["error_message"] = err_message
            self.type = "nifti"
        if is_dicom is True:
            self.info["BIDS"]["Folder"] = "sourcedata"
            self.type = "DiCOM"
            self.name = "Some -annoying _-_ DICOM_name.dicom.zip"

    def download(self, save_path):
        pass


class MockParent:
    """Mock parent class"""

    def __init__(self, parent_type):
        self.type = parent_type


class MockDest:
    """Mock destination class"""

    def __init__(self, container_type="analysis", parent_type="subject", throw_exception=False):
        if not throw_exception:
            self.container_type = container_type
        else:
            self.container_type = flywheel.rest.ApiException
        self.parent = MockParent(parent_type)
