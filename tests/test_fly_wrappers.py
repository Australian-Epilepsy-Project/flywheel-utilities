"""
Tests for fly_wrappers
"""
import logging

import flywheel
import pytest

from flywheel_utilities import fly_wrappers
from tests.mock_classes import Context, MockDest


def test_check_run_level_success(caplog, mocker):
    """Test correct run level"""

    mock_context = Context()

    mock_object = mocker.MagicMock(name="get")

    mocker.patch("tests.mock_classes.Client.get", new=mock_object)
    mock_object.return_value = MockDest()

    with caplog.at_level(logging.DEBUG):
        fly_wrappers.check_run_level(mock_context, "subject", "analysis")

    assert len(caplog.messages) == 0


def test_check_run_level_wrong_container(caplog, mocker):
    """Test wrong run level"""

    mock_context = Context()

    mock_object = mocker.MagicMock(name="get")

    mocker.patch("tests.mock_classes.Client.get", new=mock_object)
    mock_object.return_value = MockDest(container_type="not_analysis")

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(SystemExit) as err:
            fly_wrappers.check_run_level(mock_context, "subject", "analysis")

    assert err.type == SystemExit
    assert len(caplog.messages) != 0
    assert caplog.messages[0] == "The destination ID does not point to a valid analysis container"


def test_check_run_level_wrong_level(caplog, mocker):
    """Test wrong run level"""

    mock_context = Context()

    mock_object = mocker.MagicMock(name="get")

    mocker.patch("tests.mock_classes.Client.get", new=mock_object)
    mock_object.return_value = MockDest(parent_type="session")

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(SystemExit) as err:
            fly_wrappers.check_run_level(mock_context, "subject", "analysis")

    assert err.type == SystemExit
    assert len(caplog.messages) != 0
    assert caplog.messages[0] == "Destination type is session"
    assert caplog.messages[1] == "Expected subject"


def test_check_run_level_api_exception(caplog, mocker):
    """Test catching api exception"""

    mock_context = Context()

    # Patch get function to throw Exception
    mocker.patch(
        "tests.mock_classes.Client.get", side_effect=flywheel.rest.ApiException("Flywheel Error")
    )
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(SystemExit) as err:
            fly_wrappers.check_run_level(mock_context, "subject", "analysis")

    assert err.type == SystemExit
    assert caplog.messages[0] == "The destination id does not point to a valid analysis container"
    assert caplog.messages[1] == "(Flywheel Error) Reason: None"
