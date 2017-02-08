"""Tests for the dtool cli."""

import contextlib
from distutils.dir_util import copy_tree
import os
import subprocess
import shutil
import tempfile
import json

import yaml
import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "mimetype", "input", "archive")


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def chdir(request):
    d = tempfile.mkdtemp()

    cwd = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(cwd)
        shutil.rmtree(d)


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_version():

    cmd = ["dtool", "--version"]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')

    assert output.startswith('dtool, version')


def test_new_dataset(chdir):

    from click.testing import CliRunner
    from dtool.datatool.cli import dataset
    from dtool import DataSet

    runner = CliRunner()

    input_string = 'my_project\n'
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    result = runner.invoke(dataset, input=input_string)

    assert not result.exception

    assert os.path.isdir('my_dataset')
    expected_dtool_file = os.path.join('my_dataset', '.dtool', 'dtool')
    assert os.path.isfile(expected_dtool_file)

    dataset = DataSet.from_path('my_dataset')
    assert dataset.name == 'my_dataset'


def test_new_project(chdir):

    from click.testing import CliRunner
    from dtool.datatool.cli import project
    from dtool import Project

    runner = CliRunner()

    input_string = 'my_project\n'

    result = runner.invoke(project, input=input_string)

    assert not result.exception

    assert os.path.isdir('my_project')
    expected_dtool_file = os.path.join('my_project', '.dtool', 'dtool')
    assert os.path.isfile(expected_dtool_file)

    Project.from_path('my_project')


def test_new_dataset_in_project(chdir):

    from click.testing import CliRunner
    from dtool.datatool.cli import dataset, project
    from dtool import DataSet

    runner = CliRunner()

    input_string = 'new_test_project\n'

    result = runner.invoke(project, input=input_string)

    assert not result.exception

    with remember_cwd():
        os.chdir('new_test_project')
        input_string = '\n'
        input_string += 'new_test_dataset\n'
        input_string += '\n'  # confidential
        input_string += '\n'  # personally identifiable information
        input_string += 'Test User\n'
        input_string += 'test.user@example.com\n'
        input_string += 'usert\n'
        input_string += '\n'  # Date

        result = runner.invoke(dataset, input=input_string)

        assert not result.exception

    dataset = DataSet.from_path('new_test_project/new_test_dataset')

    assert dataset.descriptive_metadata['project_name'] == 'new_test_project'


def test_manifest_update(tmp_dir):

    from dtool import DataSet
    dataset = DataSet("test_dataset", "data")
    dataset.persist_to_path(tmp_dir)

    data_dir = os.path.join(tmp_dir, "data")
    copy_tree(TEST_INPUT_DATA, data_dir)

    cmd = ["dtool", "manifest", "update", tmp_dir]
    subprocess.call(cmd)
    manifest_path = os.path.join(tmp_dir, ".dtool", "manifest.json")
    assert os.path.isfile(manifest_path)

    # Ensure manifest is valid json.
    with open(manifest_path, "r") as fh:
        manifest = json.load(fh)

    file_list = manifest["file_list"]

    expected_mimetypes = {
        'actually_a_png.txt': 'image/png',
        'actually_a_text_file.jpg': 'text/plain',
        'empty_file': 'inode/x-empty',
        'random_bytes': 'application/octet-stream',
        'real_text_file.txt': 'text/plain',
        'tiny.png': 'image/png'
    }

    for file in file_list:
        file_path = file['path']
        actual = file['mimetype']
        expected = expected_mimetypes[file_path]
        assert expected == actual


def test_markup(tmp_dir):
    from click.testing import CliRunner
    from dtool.datatool.cli import markup
    from dtool import DataSet

    existing_data_dir = os.path.join(tmp_dir, 'data')

    shutil.copytree(TEST_INPUT_DATA, existing_data_dir)

    runner = CliRunner()

    input_string = 'my_project\n'
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    expected_dtool_file = os.path.join(
        existing_data_dir,
        '.dtool',
        'dtool')

    assert not os.path.isfile(expected_dtool_file)
    with remember_cwd():
        os.chdir(existing_data_dir)
        result = runner.invoke(markup, input=input_string)

        assert not result.exception

    assert os.path.isfile(expected_dtool_file)

    DataSet.from_path(existing_data_dir)

    readme_path = os.path.join(existing_data_dir, "README.yml")
    with open(readme_path) as fh:
        descriptive_metadata = yaml.load(fh)
    assert "owner_name" not in descriptive_metadata
    assert descriptive_metadata["owners"][0]["name"] == "Test User"


def test_markup_inherits_parent_metadata(tmp_dir):
    from click.testing import CliRunner
    from dtool.datatool.cli import markup
    from dtool import DataSet, Project

    project = Project("test_inheritance")
    project.persist_to_path(tmp_dir)

    existing_data_dir = os.path.join(tmp_dir, 'data')

    shutil.copytree(TEST_INPUT_DATA, existing_data_dir)

    runner = CliRunner()

    input_string = '\n'
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    expected_dtool_file = os.path.join(
        existing_data_dir,
        '.dtool',
        'dtool')

    assert not os.path.isfile(expected_dtool_file)
    with remember_cwd():
        os.chdir(existing_data_dir)
        result = runner.invoke(markup, input=input_string)

        assert not result.exception

    assert os.path.isfile(expected_dtool_file)

    readme_path = os.path.join(existing_data_dir, "README.yml")
    with open(readme_path) as fh:
        descriptive_metadata = yaml.load(fh)
    assert descriptive_metadata["project_name"] == "test_inheritance"

    dataset = DataSet.from_path(existing_data_dir)

    assert dataset.descriptive_metadata["project_name"] == "test_inheritance"
