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
