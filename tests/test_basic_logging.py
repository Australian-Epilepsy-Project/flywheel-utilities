'''
Test for basic_logging.py
'''

import logging

from flywheel_utilities.basic_logging import setup_basic_logging
from tests.mock_classes import Context

logger = logging.getLogger()


def test_setup_basic_logging(caplog):
    ''' Test setup_basic_logging '''

    context_debug = Context("DEBUG")
    with caplog.at_level(logging.INFO):
        setup_basic_logging(context_debug)

    # 30 = DEBUG
    assert logger.level == 30
    assert caplog.messages[0] == "Logger initialised"
