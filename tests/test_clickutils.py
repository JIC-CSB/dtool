"""Tests for dtool clickutils."""

import os
import shutil
import tempfile

import pytest

from dtool import Project


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_create_project(tmp_dir):
    from dtool.clickutils import create_project

    import click
    from click.testing import CliRunner

    runner = CliRunner()

    @click.command()
    def create_project_assist():
        create_project(tmp_dir)

    input_string = 'my_project\n'

    result = runner.invoke(create_project_assist, input=input_string)

    assert not result.exception

    expected_project_path = os.path.join(tmp_dir, 'my_project')
    assert os.path.isdir(expected_project_path)
    expected_dtool_file = os.path.join(
        tmp_dir, 'my_project', '.dtool', 'dtool')
    assert os.path.isfile(expected_dtool_file)

    loaded_project = Project.from_path(expected_project_path)
    assert len(loaded_project.uuid) == 36
    assert loaded_project.descriptive_metadata['project_name'] == 'my_project'
