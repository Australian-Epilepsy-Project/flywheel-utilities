'''
General functions.
'''

import logging

log = logging.getLogger(__name__)


def get_gear_name(context):
    '''
    Get gear name and version.

    Args:
        context (GearToolkitContext): flywheel gear context object
    Returns:
        gear_name (str): <gear_name>:<version>
    '''

    gear_name = context.manifest['label']
    gear_name += ":"
    gear_name += context.manifest['version']

    return gear_name


def zip_save_name(identifier, sub_label, dest_id):
    '''
    Construct name of output zip file

    Args:
        identifier (str): base save name
        sub_label (str): subject label <sub-XXXXXX>
        dest_id (str): analysis destination ID
    '''

    save_name = identifier + '_'
    save_name += sub_label + '_' + dest_id

    return save_name + '.zip'
