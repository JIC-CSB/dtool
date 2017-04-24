"""Tests for the dtool cli."""

from distutils.dir_util import copy_tree
import os
import subprocess
import shutil
import json

import yaml

from . import tmp_dir_fixture  # NOQA
from . import chdir_fixture  # NOQA
from . import remember_cwd

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "mimetype", "input", "archive")


def test_version():

    cmd = ["dtool", "--version"]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')

    assert output.startswith('dtool, version')


def test_info(chdir_fixture):  # NOQA

    # In a clean directory.
    cmd = ["dtool", "info"]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')

    assert output.startswith('Directory is not a dtool object')

    # Turn directory into a dataset.
    from dtoolcore import DataSet
    dataset = DataSet("testing")
    dataset.persist_to_path(".")

    cmd = ["dtool", "info"]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')
    assert output.startswith('Directory is a dtool dataset')


def test_info_with_dataset_path(tmp_dir_fixture):  # NOQA

    # Turn directory into a dataset.
    from dtoolcore import DataSet
    dataset = DataSet("testing")
    dataset.persist_to_path(tmp_dir_fixture)

    cmd = ["dtool", "info", tmp_dir_fixture]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')
    assert output.startswith('Directory is a dtool dataset')


def test_new_dataset(chdir_fixture):  # NOQA

    from click.testing import CliRunner
    from dtool.cli import dataset
    from dtoolcore import DataSet

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
    assert dataset.manifest["hash_function"] == "shasum"

    overlays = dataset.access_overlays()
    assert "mimetype" in overlays


def test_new_project(chdir_fixture):  # NOQA

    from click.testing import CliRunner
    from dtool.cli import project
    from dtool.project import Project

    runner = CliRunner()

    input_string = 'my_project\n'

    result = runner.invoke(project, input=input_string)

    assert not result.exception

    assert os.path.isdir('my_project')
    expected_dtool_file = os.path.join('my_project', '.dtool', 'dtool')
    assert os.path.isfile(expected_dtool_file)

    Project.from_path('my_project')


def test_new_dataset_in_project(chdir_fixture):  # NOQA

    from click.testing import CliRunner
    from dtool.cli import dataset, project
    from dtoolcore import DataSet

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


def test_manifest_update(tmp_dir_fixture):  # NOQA

    from dtoolcore import DataSet
    dataset = DataSet("test_dataset", "data")
    dataset.persist_to_path(tmp_dir_fixture)

    data_dir = os.path.join(tmp_dir_fixture, "data")
    copy_tree(TEST_INPUT_DATA, data_dir)

    cmd = ["dtool", "manifest", "update", tmp_dir_fixture]
    subprocess.call(cmd)
    manifest_path = os.path.join(tmp_dir_fixture, ".dtool", "manifest.json")
    assert os.path.isfile(manifest_path)

    # Ensure manifest is valid json.
    with open(manifest_path, "r") as fh:
        manifest = json.load(fh)

    file_list = manifest["file_list"]
    assert len(file_list) == 6

    ds = DataSet.from_path(tmp_dir_fixture)
    overlays = ds.access_overlays()
    assert "mimetype" in overlays
    assert len(overlays["mimetype"]) == 6
    identifier = "09648d19e11f0b20e5473594fc278afbede3c9a4"
    assert overlays["mimetype"][identifier] == "image/png"


def test_markup(tmp_dir_fixture):  # NOQA
    from click.testing import CliRunner
    from dtool.cli import markup
    from dtoolcore import DataSet

    existing_data_dir = os.path.join(tmp_dir_fixture, 'data')

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

    readme_path = os.path.join(existing_data_dir, "README.yml")
    with open(readme_path) as fh:
        descriptive_metadata = yaml.load(fh)
    assert "owner_name" not in descriptive_metadata
    assert descriptive_metadata["owners"][0]["name"] == "Test User"

    ds = DataSet.from_path(existing_data_dir)
    overlays = ds.access_overlays()
    assert "mimetype" in overlays
    assert len(overlays["mimetype"]) == 6
    identifier = "09648d19e11f0b20e5473594fc278afbede3c9a4"
    assert overlays["mimetype"][identifier] == "image/png"


def test_markup_default_hash_function(chdir_fixture):  # NOQA
    from click.testing import CliRunner
    from dtool.cli import markup
    from dtoolcore import DataSet

    runner = CliRunner()

    input_string = 'my_project\n'
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    result = runner.invoke(markup, input=input_string)
    assert not result.exception

    dataset = DataSet.from_path('.')
    assert dataset.manifest["hash_function"] == "shasum"

    overlays = dataset.access_overlays()
    assert "mimetype" in overlays


def test_markup_alt_dir(tmp_dir_fixture):  # NOQA
    from click.testing import CliRunner
    from dtool.cli import markup
    from dtoolcore import DataSet

    runner = CliRunner()

    input_string = 'my_project\n'
    input_string += 'my_dataset\n'
    input_string += '\n'  # confidential
    input_string += '\n'  # personally identifiable information
    input_string += 'Test User\n'
    input_string += 'test.user@example.com\n'
    input_string += 'usert\n'
    input_string += '\n'  # Date

    result = runner.invoke(
        markup,
        args=[tmp_dir_fixture],
        input=input_string)
    assert not result.exception

    dataset = DataSet.from_path(tmp_dir_fixture)
    assert dataset.manifest["hash_function"] == "shasum"


def test_markup_inherits_parent_metadata(tmp_dir_fixture):  # NOQA
    from click.testing import CliRunner
    from dtool.cli import markup
    from dtoolcore import DataSet
    from dtool.project import Project

    project = Project("test_inheritance")
    project.persist_to_path(tmp_dir_fixture)

    existing_data_dir = os.path.join(tmp_dir_fixture, 'data')

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
