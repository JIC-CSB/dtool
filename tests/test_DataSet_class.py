"""Test the dtool.DataSet class."""

import os
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


@pytest.fixture
def chdir(request):
    d = tempfile.mkdtemp()

    cwd = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(cwd)
        shutil.rmtree(d)


def test_dataset_initialisation():
    from dtool import DataSet

    dataset = DataSet(name='my_dataset')
    assert dataset.name == 'my_dataset'
    assert len(dataset.uuid) == 36
    assert dataset._admin_metadata['type'] == 'dataset'
    assert dataset._admin_metadata['manifest_root'] == '.'
    assert isinstance(dataset.dtool_version, str)
    assert isinstance(dataset.unix_username, str)
    assert dataset.readme_path == None


def test_initialise_alternative_manifest_root():
    from dtool import DataSet

    dataset = DataSet('my_dataset', data_directory='archive')

    assert dataset._admin_metadata['manifest_root'] == 'archive'


def test_cannot_change_uuid_or_name():
    from dtool import DataSet

    dataset = DataSet(name='my_dataset')

    with pytest.raises(AttributeError):
        dataset.uuid = None

    with pytest.raises(AttributeError):
        dataset.name = None


def test_dataset_persist_to_path(tmp_dir):
    from dtool import DataSet
    dataset = DataSet('my_dataset')

    expected_dtool_dir = os.path.join(tmp_dir, '.dtool')
    expected_dtool_file = os.path.join(expected_dtool_dir, 'dtool')
    assert not os.path.isdir(expected_dtool_dir)
    assert not os.path.isfile(expected_dtool_file)

    dataset.persist_to_path(tmp_dir)
    assert os.path.isdir(expected_dtool_dir)
    assert os.path.isfile(expected_dtool_file)

    import json
    with open(expected_dtool_file) as fh:
        admin_metadata = json.load(fh)
    assert admin_metadata['type'] == 'dataset'
    assert dataset._admin_metadata == admin_metadata

    expected_readme_path = os.path.join(tmp_dir, 'README.yml')
    assert os.path.isfile(expected_readme_path)


def test_persist_to_path_updates_readme_path(tmp_dir):
    from dtool import DataSet

    dataset = DataSet('my_dataset')

    assert dataset.readme_path is None

    dataset.persist_to_path(tmp_dir)

    expected_readme_path = os.path.join(tmp_dir, 'README.yml')
    assert dataset.readme_path == expected_readme_path


def test_creation_of_data_dir(tmp_dir):
    from dtool import DataSet
    dataset = DataSet('my_dataset', data_directory='data')

    expected_data_directory = os.path.join(tmp_dir, 'data')
    assert not os.path.isdir(expected_data_directory)

    dataset.persist_to_path(tmp_dir)
    assert os.path.isdir(expected_data_directory)


def test_multiple_persist_to_path_raises(tmp_dir):
    from dtool import DataSet

    dataset = DataSet('my_dataset')

    dataset.persist_to_path(tmp_dir)

    with pytest.raises(OSError):
        dataset.persist_to_path(tmp_dir)
