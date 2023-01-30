"""
Very basic mock context class
"""

from pathlib import Path


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# Mock context manager
class Context:
    """Dummy class docstring"""

    def __init__(
        self,
        debug_level="INFO",
        working_dir="",
        gear_name="dummy-name",
        gear_version="3.14.2_0.11.0",
        fs_license=True,
    ):
        self.config = {"gear-log-level": debug_level}
        self.work_dir = Path(working_dir)
        self.manifest = {"label": gear_name, "version": gear_version}
        self.destination = {"id": "tests"}
        self.fs_license = fs_license
        self.client = Client(self.fs_license)


class Client:
    """Dummy class docstring"""

    def __init__(self, fs_license: bool = True):
        self.fs_license = fs_license

    def get_analysis(self, _i):
        """Mock call"""
        dummy_dict = {"parents": {"project": "unit_tests"}}
        return dummy_dict

    def get_project(self, _j):
        """Mock call"""
        if self.fs_license:
            return {"info": {"FREESURFER_LICENSE": "insert_license"}}

        return {"info": {}}
