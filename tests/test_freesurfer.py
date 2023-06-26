"""
Tests for freesurfer.py
"""

import logging

import pytest

from flywheel_utilities import freesurfer
from tests.mock_classes import Context


def test_install_license_no_env_set(caplog, mocker):
    """Test when $FREESURFER is not set."""

    # Mock the call to act as if $FREESURFER_HOME is not set
    mocker.patch("os.getenv", return_value=None)

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(AssertionError) as err_assert:
            freesurfer.install_freesurfer_license(1)

    assert (
        str(err_assert.value)
        == "Must set $FREESURFER_HOME before calling install_freesurfer_license()"
    )


def test_install_free_license_success(caplog, tmp_path, mocker):
    """Test when $FREESURFER is correctly set."""
    # Freesurfer directory
    dir_fs = tmp_path / "fs_dir"
    dir_fs.mkdir(exist_ok=False)

    # Mock the ENV call
    mocker.patch("os.getenv", return_value=str(dir_fs))

    context = Context()

    with caplog.at_level(logging.DEBUG):
        freesurfer.install_freesurfer_license(context)

    assert (dir_fs / "license.txt").is_file() is True
    assert caplog.messages[0] == "Using FreeSurfer license in project info."


def test_install_free_license_not_found(caplog, tmp_path, mocker):
    """Test when license is not found"""

    dir_fs = tmp_path / "fs_dir"
    # Mock the ENV call
    mocker.patch("os.getenv", return_value=str(dir_fs))

    context = Context(fs_licence=False)

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(FileNotFoundError) as err_unlocated:
            freesurfer.install_freesurfer_license(context)

    assert (dir_fs / "license.txt").is_file() is False
    assert str(err_unlocated.value) == "Freesurfer license could not be located"
