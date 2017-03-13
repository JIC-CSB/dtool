"""Tests for dtool."""

import shutil
import tempfile

import pytest


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_version_is_str():
    from dtool import __version__
    assert isinstance(__version__, str)


def test_metadata_from_path(tmp_dir):
    from dtool.metadata import metadata_from_path

    assert metadata_from_path(tmp_dir) == {}

    from dtool.project import Project
    project = Project("my_project")
    project.persist_to_path(tmp_dir)

    assert metadata_from_path(tmp_dir) == {"project_name": "my_project"}
