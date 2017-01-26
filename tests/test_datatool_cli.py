"""Tests for the dtool cli."""

import os
import subprocess
import shutil
import tempfile
import json

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "mimetype", "input", "archive")


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

    cmd = ["datatool", "--version"]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')

    assert output.startswith('datatool, version')


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


def test_manifest_create(tmp_dir):

    data_dir = os.path.join(tmp_dir, "data")
    shutil.copytree(TEST_INPUT_DATA, data_dir)

    cmd = ["datatool", "manifest", "create", data_dir]
    subprocess.call(cmd)
    manifest_path = os.path.join(tmp_dir, "manifest.json")
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
