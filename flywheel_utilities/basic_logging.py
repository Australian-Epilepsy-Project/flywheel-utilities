'''
Setup basic logging with the log level determined from the Flywheel manifest
variable 'gear-log-level'.
'''

import logging


def setup_basic_logging(context,
                        log_format='[%(asctime)s %(levelname)s] %(message)s',
                        log_date='%Y-%m-%d %H:%M:%S'):
    '''
    Args:
        context (flywheel_gear_toolkit.GearToolkitContext): context object
        log_format (str): logging print format
        log_date (str): logging date format
    '''

    # Setup basic logging
    if 'gear-log-level' in context.config:
        if context.config['gear-log-level'] == 'DEBUG':
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level,
                        format=log_format,
                        datefmt=log_date)

    logger = logging.getLogger()
    logger.info("Logger initialised")
