
'''
Test for bids.py
'''

# pylint: disable=import-error
import logging
import pytest
from flywheel_utilities import bids
from tests.mock_classes import Context


def test_add_dataset_description(tmp_path, caplog):
    ''' Test add_dataset_desctiption '''

    with caplog.at_level(logging.INFO):
        bids.add_dataset_description(tmp_path)

    # Dummy dataset description
    desc_file = tmp_path / "dataset_description.json"

    # Check file has been written
    assert desc_file.exists() is True

    # Check file has expected contents
    with desc_file.open() as in_file:
        line = in_file.read().splitlines()
        assert line[6] == '    "BIDSVersion": "1.2.0",'

    # Check README was created
    readme = tmp_path / "README"
    assert readme.exists() is True

    # Check contents of README
    with readme.open() as in_file:
        line = in_file.read().splitlines()
        assert line[120] == "Lorem ipsum"

    msg = "Dummy dataset_description.json created in root bids directory"
    assert caplog.messages[0] == msg


def test_create_deriv_dir_first_ver(tmp_path, caplog):
    ''' Test create_deriv_dir '''

    gear_name = 'testing-gear'
    gear_version = '3.14.2_0.11.0'
    first_ver = gear_version[:gear_version.find("_")]
    label = '101101'

    context = Context(working_dir=tmp_path,
                      gear_name=gear_name,
                      gear_version=gear_version)

    # Use first version for dir creation
    with caplog.at_level(logging.INFO):
        bids.create_deriv_dir(context, label, "first")

    bids_dir = tmp_path / (gear_name+"-v"+first_ver+"/sub-"+label)

    assert bids_dir.exists() is True

    assert caplog.messages[0] == f"Created BIDs derivative directory: {bids_dir}"


def test_create_deriv_dir_second_ver(tmp_path, caplog):
    ''' Test create_deriv_dir '''

    gear_name = 'testing-gear'
    gear_version = '3.14.2_0.11.0'
    second_ver = gear_version[gear_version.find("_")+1:]
    label = '101101'

    context = Context(working_dir=tmp_path,
                      gear_name=gear_name,
                      gear_version=gear_version)
    # Use second version for dir creation
    with caplog.at_level(logging.INFO):
        bids.create_deriv_dir(context, label, "second")

    bids_dir = tmp_path / (gear_name+"-v"+second_ver+"/sub-"+label )

    assert bids_dir.exists() is True

    assert caplog.messages[0] == f"Created BIDs derivative directory: {bids_dir}"


def test_fail_create_deriv_dir(tmp_path, caplog):
    ''' Test create_deriv_dir '''

    gear_name = 'testing-gear'
    gear_version = '3.a14.2_0.11a.0'
    first_ver = gear_version[:gear_version.find("_")]
    label = '101101'

    context = Context(working_dir=tmp_path,
                      gear_name=gear_name,
                      gear_version=gear_version)

    # Use second version for dir creation
    caplog.at_level(logging.INFO)
    with pytest.raises(SystemExit) as pytest_wrapped_err:
        bids.create_deriv_dir(context, label, "first")

    bids_dir = tmp_path / (gear_name+"-v"+first_ver+"/sub-"+label )

    assert pytest_wrapped_err.type == SystemExit
    assert pytest_wrapped_err.value.code == 1

    assert bids_dir.exists() is False

    assert caplog.messages[0] == ("Could not isolate Flywheel versioning in "
                                  "gear name when trying to strip it for BIDs "
                                  "derivative directory")
