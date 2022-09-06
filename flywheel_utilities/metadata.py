'''
Tag subjects with the gear and version number
'''

import logging
import sys
# pylint: disable=import-error
import flywheel
# pylint: enable=import-error

from flywheel_utilities import utils

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


def update_subject_tags(context, subject):
    '''
    Update the subject's tag to indicate the gear has been run

    Args:
        context (flywheel_gear_toolkit.GearToolkitContext): gear context object
        subject (flywheel.models.Subject): flywheel subject object
    '''

    gear_name = utils.get_gear_name(context)

    if gear_name not in subject.tags:

        try:
            context.client.add_subject_tag(subject.id, gear_name)
        except flywheel.rest.ApiException as err:
            log.error(f"{err}")
            sys.exit(1)

        log.info(f"Subject's tags now include '{gear_name}'")
