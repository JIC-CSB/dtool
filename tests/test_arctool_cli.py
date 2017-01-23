"""Tests for the arctool cli."""

import os
import tempfile
import shutil
import subprocess
import contextlib
from distutils.dir_util import copy_tree

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "basic", "output")


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


def test_full_archiving_workflow(chdir):

    from click.testing import CliRunner
    from dtool.arctool.cli import dataset

    runner = CliRunner()

    input_string = 'some_project\n'
    input_string += 'data_set_1\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    result = runner.invoke(dataset, input=input_string)

    assert not result.exception

    assert os.path.isdir('data_set_1')
    assert os.path.isdir('data_set_1/.dtool')
    assert os.path.isfile('data_set_1/.dtool/dtool')

    dataset_path = 'data_set_1'

    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(dataset_path, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    cmd = ["arctool", "--version"]
    subprocess.call(cmd)

    cmd = ["arctool", "manifest", "create", archive_output_path]
    subprocess.call(cmd)
    manifest_path = os.path.join(dataset_path, "manifest.json")
    assert os.path.isfile(manifest_path)

    cmd = ["arctool", "archive", "create", dataset_path]
    subprocess.call(cmd)
    tar_path = "data_set_1.tar"
    assert os.path.isfile(tar_path)

    cmd = ["arctool", "archive", "compress", tar_path]
    subprocess.call(cmd)
    gzip_path = "data_set_1.tar.gz"
    assert os.path.isfile(gzip_path)

    # Remove the dataset path to ensure that files are actually extracted.
    shutil.rmtree(dataset_path)

    cmd = ["arctool", "extract", "readme", gzip_path]
    subprocess.call(cmd)
    readme_path = os.path.join(dataset_path, "README.yml")
    assert os.path.isfile(readme_path)

    cmd = ["arctool", "extract", "manifest", gzip_path]
    subprocess.call(cmd)
    manifest_path = os.path.join(dataset_path, ".dtool/manifest.json")
    assert os.path.isfile(manifest_path)

    cmd = ["arctool", "verify", "summary", gzip_path]
    subprocess.call(cmd)


def test_new(chdir):

    from click.testing import CliRunner
    from dtool.arctool.cli import new
    from dtool import DataSet

    runner = CliRunner()

    input_string = 'my_test_project\n'
    input_string += '\n'  # prompting for project with create dataset
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    result = runner.invoke(new, input=input_string)

    assert not result.exception

    assert os.path.isfile('my_test_project/.dtool-collection')
    assert os.path.isdir('my_test_project/my_dataset')
    assert os.path.isdir('my_test_project/my_dataset/.dtool')
    assert os.path.isfile('my_test_project/my_dataset/.dtool/dtool')
    assert os.path.isfile('my_test_project/my_dataset/.dtool/manifest.json')
    assert os.path.isfile('my_test_project/my_dataset/README.yml')

    DataSet.from_path('my_test_project/my_dataset')

    # TODO - fix this!
    # assert dataset.descriptive_metadata['project_name'] == 'my_test_project'


def test_new_dataset(chdir):

    from click.testing import CliRunner
    from dtool.arctool.cli import dataset

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
    assert os.path.isdir('my_dataset/.dtool')
    assert os.path.isfile('my_dataset/.dtool/dtool')
    assert os.path.isfile('my_dataset/.dtool/manifest.json')


def test_new_project(chdir):

    from click.testing import CliRunner
    from dtool.arctool.cli import project

    runner = CliRunner()

    input_string = 'my_test_project\n'

    result = runner.invoke(project, input=input_string)

    assert not result.exception

    assert os.path.isdir('my_test_project')
    assert os.path.isfile('my_test_project/.dtool-collection')
    assert os.path.isfile('my_test_project/README.yml')


def test_create_new_datasets_within_existing_project(chdir):

    from click.testing import CliRunner
    from dtool.arctool.cli import new

    runner = CliRunner()

    input_string = 'my_test_project\n'
    input_string += '\n'  # prompting for project with create dataset
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    result = runner.invoke(new, input=input_string)

    with remember_cwd():
        os.chdir('my_test_project')

        input_string = '\n'  # prompting for project
        input_string += 'my_second_dataset\n'
        input_string += '\n'  # confidential
        input_string += '\n'  # personally identifiable information
        input_string += 'Test User\n'
        input_string += 'test.user@example.com\n'
        input_string += 'usert\n'
        input_string += '\n'  # Date
        result = runner.invoke(new, input=input_string)

        assert not result.exception
