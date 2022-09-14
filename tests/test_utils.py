'''
Test for utils.py
'''


from flywheel_utilities import utils
from tests.mock_classes import Context


def test_get_gear_name():
    ''' Test get_gear_name '''

    gear_name = 'testing-gear'
    gear_version = '3.14.2_0.11.0'

    context = Context(gear_name=gear_name,
                      gear_version=gear_version)

    assert utils.get_gear_name(context) == gear_name+":"+gear_version


def test_zip_save_name():
    ''' Test zip_save_name '''

    base = 'test-identifier'
    label = 'sub-101101'
    dest = "12321ab2345e8de8f"

    assert utils.zip_save_name(base, label, dest) == base+'_'+label+'_'+dest+'.zip'
