"""Test the dtool.DataSet class."""

import os
import json
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
    expected_manifest_path = os.path.join('.dtool', 'manifest.json')
    assert dataset._admin_metadata['manifest_path'] == expected_manifest_path
    assert dataset._abs_manifest_path is None
    assert isinstance(dataset.dtool_version, str)
    assert isinstance(dataset.unix_username, str)
    assert dataset.abs_readme_path is None


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

    expected_manifest_path = os.path.join(tmp_dir, '.dtool', 'manifest.json')
    assert os.path.isfile(expected_manifest_path)


def test_persist_to_path_updates_abs_readme_path(tmp_dir):
    from dtool import DataSet

    dataset = DataSet('my_dataset')

    assert dataset.abs_readme_path is None

    dataset.persist_to_path(tmp_dir)

    expected_abs_readme_path = os.path.join(tmp_dir, 'README.yml')
    assert dataset.abs_readme_path == expected_abs_readme_path


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


def test_persist_to_path_sets_abs_paths(tmp_dir):
    from dtool import DataSet

    dataset = DataSet('my_dataset')

    expected_abs_readme_path = os.path.join(tmp_dir, 'README.yml')
    expected_abs_manifest_path = os.path.join(tmp_dir,
        '.dtool', 'manifest.json')

    assert dataset.abs_readme_path is None
    assert dataset._abs_manifest_path is None

    dataset.persist_to_path(tmp_dir)

    assert dataset.abs_readme_path == expected_abs_readme_path
    assert dataset._abs_manifest_path == expected_abs_manifest_path


def test_equality():
    from copy import deepcopy
    from dtool import DataSet
    dataset = DataSet('my_dataset')
    dataset_again = deepcopy(dataset)
    assert dataset_again == dataset

    # We should never do this!
    dataset_again._admin_metadata['name'] = 'nonsense'
    assert dataset_again != dataset


def test_do_not_overwrite_existing_readme(chdir):
    from dtool import DataSet

    dataset = DataSet('my_dataset')

    readme_contents = "---\nproject_name: test_project\n"

    with open('README.yml', 'w') as fh:
        fh.write(readme_contents)

    dataset.persist_to_path('.')

    with open('README.yml') as fh:
        actual_contents = fh.read()

    assert actual_contents == readme_contents


def test_manifest_generation(chdir):
    from dtool import DataSet

    dataset = DataSet('my_dataset')

    with open('README.yml', 'w') as fh:
        fh.write('---')
        fh.write('project_name: test_project')

    with open('test_file.txt', 'w') as fh:
        fh.write('Hello world')

    dataset.persist_to_path('.')

    expected_manifest_path = os.path.join('.dtool', 'manifest.json')

    with open(expected_manifest_path) as fh:
        manifest = json.load(fh)

    file_list = manifest['file_list']
    keyed_by_path = {entry['path']: entry for entry in file_list}

    assert 'file_list' in manifest
    assert len(manifest['file_list']) == 2
    assert 'test_file.txt' in keyed_by_path
    assert keyed_by_path['test_file.txt']['size'] == 11
    assert keyed_by_path['README.yml']['size'] == 29


def test_dataset_from_path(tmp_dir):
    pass
