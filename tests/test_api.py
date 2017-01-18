"""Tests for dtool."""

import os
import shutil
import tempfile
from distutils.dir_util import copy_tree

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


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


def create_persisted_archive_dataset(path):
    from dtool import DataSet
    from jinja2 import Environment, PackageLoader

    readme_info = [
        ("project_name", u"my_project"),
        ("dataset_name", u"brassica_rnaseq_reads"),
        ("confidential", False),
        ("personally_identifiable_information", False),
        ("owner_name", u"Your Name"),
        ("owner_email", u"your.email@example.com"),
        ("unix_username", u"namey"),
        ("archive_date", u"2017-01-01"),
    ]

    descriptive_metadata = dict(readme_info)

    dataset = DataSet(descriptive_metadata['dataset_name'], manifest_root='archive')
    dataset.descriptive_metadata = descriptive_metadata
    env = Environment(loader=PackageLoader('dtool', 'templates'),
                      keep_trailing_newline=True)
    readme_template = env.get_template('arctool_dataset_README.yml')
    dataset_path = dataset.persist_to_path(path,
                                           readme_template=readme_template)

    return dataset, dataset_path


def test_version_is_str():
    from dtool import __version__
    assert isinstance(__version__, str)


def test_dataset_initialisation():

    from dtool import DataSet

    test_dataset = DataSet('my_dataset')

    assert len(test_dataset.uuid) == 36
    assert test_dataset.name == 'my_dataset'
    assert test_dataset.manifest_root == 'data'
    assert test_dataset.admin_metadata == {'dataset_name': 'my_dataset',
                                           'type': 'dataset'}
    assert test_dataset.descriptive_metadata == {'dataset_name': 'my_dataset'}

    test_dataset = DataSet('my_dataset', manifest_root='archive')

    assert test_dataset.manifest_root == 'archive'


def test_dataset_admin_metadata(chdir):

    from dtool import DataSet

    setup_dataset = DataSet('my_dataset')
    setup_dataset.persist_to_path('.')

    test_dataset = DataSet.from_path('my_dataset')

    expected_readme_path = 'README.yml'
    assert test_dataset.admin_metadata['readme_path'] == expected_readme_path


def test_dataset_persist_to_path(tmp_dir):

    from dtool import DataSet

    test_dataset = DataSet('my_dataset')

    with pytest.raises(AttributeError):
        test_dataset.readme_path

    with pytest.raises(AttributeError):
        test_dataset.dataset_path

    dataset_path = test_dataset.persist_to_path(tmp_dir)
    assert os.path.isdir(dataset_path)

    expected_dataset_path = os.path.join(tmp_dir, 'my_dataset')
    assert dataset_path == expected_dataset_path

    expected_dataset_info_path = os.path.join(dataset_path, '.dtool-dataset')
    assert os.path.isfile(expected_dataset_info_path)

    expected_readme_path = os.path.join(dataset_path, 'README.yml')
    assert os.path.isfile(expected_readme_path)
    assert test_dataset.readme_path == expected_readme_path

    manifest_root = os.path.join(dataset_path, test_dataset.manifest_root)
    assert os.path.isdir(manifest_root)


def test_dataset_persist_to_path_raises_runtimeerror_if_path_exists(tmp_dir):

    from dtool import DataSet

    dataset_clash_path = os.path.join(tmp_dir, 'my_dataset')
    os.mkdir(dataset_clash_path)

    test_dataset = DataSet('my_dataset')
    with pytest.raises(OSError):
        test_dataset.persist_to_path(tmp_dir)


def test_dataset_from_path(tmp_dir):

    from dtool.arctool import (
        create_manifest,
    )

    dataset, tmp_dataset = create_persisted_archive_dataset(tmp_dir)
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_dataset, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_dataset, "archive/"))

    from dtool import DataSet

    dataset = DataSet.from_path(tmp_dataset)

    assert dataset.name == 'brassica_rnaseq_reads'
    assert len(dataset.uuid) == 36
    assert dataset.readme_path == os.path.join(tmp_dataset, 'README.yml')

    assert dataset.admin_metadata['type'] == 'dataset'

    assert 'dataset_name' in dataset.descriptive_metadata
    assert 'project_name' in dataset.descriptive_metadata
    assert 'archive_date' in dataset.descriptive_metadata
