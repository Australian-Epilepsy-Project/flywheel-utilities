'''
Very basic mock context class
'''

from pathlib import Path


# pylint: disable=too-few-public-methods
# Mock context manager
class Context():
    ''' Dummy class docstring '''
    def __init__(self,
                 debug_level="INFO",
                 working_dir="",
                 gear_name="dummy-name",
                 gear_version="3.14.2_0.11.0"):
        self.config = {"gear-log-level": debug_level}

        self.work_dir = Path(working_dir)

        self.manifest = {"label": gear_name,
                         "version": gear_version}

class mock_scan():
    ''' Dummy scan docstring '''
    def __init__(self,
                 filename,
                 folder,
                 path,
                 ignore,
                 valid,
                 file_type):
        self.info = {"BIDS": {"Filename": filename,
                              "Folder": folder,
                              "Path": path,
                              "ignore": ignore,
                              "valid": valid}}
        self.type = file_type

    def download(self, dl_path):
        ''' dummy download '''
        pass
