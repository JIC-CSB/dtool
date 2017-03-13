"""Tests for dtool clickutils."""

import os

import pytest

from dtool.project import Project

from . import tmp_dir_fixture  # NOQA


def test_create_project(tmp_dir_fixture):  # NOQA
    from dtool.clickutils import create_project

    import click
    from click.testing import CliRunner

    runner = CliRunner()

    @click.command()
    def create_project_assist():
        create_project(tmp_dir_fixture)

    input_string = 'my_project\n'

    result = runner.invoke(create_project_assist, input=input_string)

    assert not result.exception

    expected_project_path = os.path.join(tmp_dir_fixture, 'my_project')
    assert os.path.isdir(expected_project_path)
    expected_dtool_file = os.path.join(
        tmp_dir_fixture, 'my_project', '.dtool', 'dtool')
    assert os.path.isfile(expected_dtool_file)

    loaded_project = Project.from_path(expected_project_path)
    assert len(loaded_project.uuid) == 36
    assert loaded_project.descriptive_metadata['project_name'] == 'my_project'


def test_info_from_path_on_not_dtool_object(tmp_dir_fixture):  # NOQA
    from dtool.clickutils import info_from_path
    assert "Directory is not a dtool object" == info_from_path(tmp_dir_fixture)


def test_info_from_path_raises_on_file(tmp_dir_fixture):  # NOQA
    from dtool.clickutils import info_from_path
    sample_data_fpath = os.path.join(tmp_dir_fixture, "data.txt")
    with open(sample_data_fpath, "w") as fh:
        fh.write("Hello")

    with pytest.raises(OSError):
        info_from_path(sample_data_fpath)


def test_info_from_path_on_dataset(tmp_dir_fixture):  # NOQA
    from dtool import DataSet
    from dtool.clickutils import info_from_path

    dataset = DataSet("mydataset")
    dataset.persist_to_path(tmp_dir_fixture)

    "Directory is a dtool dataset" == info_from_path(tmp_dir_fixture)
