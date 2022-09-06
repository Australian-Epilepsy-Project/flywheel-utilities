'''
Simple wrappers to use Flywheel.
- get_subject()
- check_run_level()
'''

import logging
import sys
# pylint: disable=import-error
import flywheel
# pylint: enable=import-error

log = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


def get_subject(context):
    '''
    Retrieve flywheel subject object

    Args:
        context (flywheel_gear_toolkit.GearToolkitContext): gear context object
    Returns:
        subject (flywheel.models.Subject): flywheel subject object
    '''

    destination = context.client.get(context.destination['id'])
    subject = context.client.get(destination.parent['id'])

    log.info(f"Subject {subject.label} retrieved")

    return subject


def check_run_level(context, which_level, gear_type='analysis'):
    '''
    Check at which level the gear is being run and cross check with the
    supplied which_level string. By default, the gear will also be checked
    that it is running at the analysis level. This can be overridden via the
    gear_type argument.

    Args:
        context (flywheel_gear_toolkit.GearToolkitContext): gear context object
        which_level (str): which level should the gear be run at
        gear_type (string): analysis or utility gear
    '''

    try:
        destination = context.client.get(context.destination['id'])
    except flywheel.ApiException as err:
        log.error("The destination id does not point to a valid "
                  "analysis container")
        log.error(f"{err}")
        sys.exit(1)

    if destination.container_type != gear_type:
        log.error("The destination ID does not point to a valid "
                  f"{gear_type} container")
        sys.exit(1)

    if destination.parent.type != which_level:
        log.error(f"Destination type is {destination.parent.type}")
        log.error(f"Expected {which_level}")
        sys.exit(1)
