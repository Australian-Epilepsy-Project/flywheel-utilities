
'''
Test for bids.py
'''

from flywheel_utilities import bids

from tests.mock_classes import Context

def test_add_dataset_description(tmp_path):
    ''' Test add_dataset_desctiption '''

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


def test_create_deriv_dir(tmp_path):
    ''' Test create_deriv_dir '''

    gear_name = 'testing-gear'
    gear_version = '3.14.2_0.11.0'
    first_ver = gear_version[:gear_version.find("_")]
    second_ver = gear_version[gear_version.find("_")+1:]
    label = '101101'

    context = Context(working_dir=tmp_path,
                      gear_name=gear_name,
                      gear_version=gear_version)

    # Use first version for dir creation
    bids.create_deriv_dir(context, label, "first")

    assert (tmp_path / (gear_name+"-v"+first_ver+"/sub-"+label)).exists() is True

    # Use second version for dir creation
    bids.create_deriv_dir(context, label, "second")

    assert (tmp_path / (gear_name+"-v"+second_ver+"/sub-"+label)).exists() is True
