"""
Tests for metadata.py
"""
import logging

from flywheel_utilities.metadata import update_subject_tags
from tests.mock_classes import Context, MockSubject


def test_update_subject_tag_exists(caplog):
    """Test updating tags when already exists"""

    # Mock context and subject
    context = Context(gear_name="megre2swi", gear_version="1.1.1")
    subject = MockSubject()

    with caplog.at_level(logging.INFO):
        update_subject_tags(context, subject)

    assert len(caplog.messages) == 0


def test_update_subject_tag_not_exists(caplog):
    """Test updating tags when already exists"""

    gear_name = "fMRIPrep"
    gear_version = "1.1.1"

    # Mock context and subject
    context = Context(gear_name=gear_name, gear_version=gear_version)
    subject = MockSubject()

    with caplog.at_level(logging.INFO):
        update_subject_tags(context, subject)

    assert caplog.messages[0] == f"Subject's tags now include '{gear_name}:{gear_version}'"
