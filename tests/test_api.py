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


def test_version_is_str():
    from dtool import __version__
    assert isinstance(__version__, str)


def test_dataset_initialisation():

    from dtool import DataSet

    test_dataset = DataSet('my_dataset')

    assert len(test_dataset.uuid) == 36
    assert test_dataset.name == 'my_dataset'
    assert test_dataset.manifest_root == 'data'
    assert test_dataset.descriptive_metadata == {'dataset_name': 'my_dataset'}

    test_dataset = DataSet('my_dataset', manifest_root='archive')

    assert test_dataset.manifest_root == 'archive'


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


def test_dataset_persist_to_path_raises_runtimeerror_if_path_exists(tmp_dir):

    from dtool import DataSet

    dataset_clash_path = os.path.join(tmp_dir, 'my_dataset')
    os.mkdir(dataset_clash_path)

    test_dataset = DataSet('my_dataset')
    with pytest.raises(OSError):
        test_dataset.persist_to_path(tmp_dir)


def test_dataset_from_path(tmp_dir):

    from dtool.arctool import (
        new_archive_dataset,
        create_manifest,
    )

    tmp_dataset = new_archive_dataset(tmp_dir, no_input=True)
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_dataset, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_dataset, "archive/"))

    from dtool import DataSet

    dataset = DataSet.from_path(tmp_dataset)

    assert dataset.name == 'brassica_rnaseq_reads'
    assert len(dataset.uuid) == 36
    assert dataset.readme_file == os.path.join(tmp_dataset, 'README.yml')

    assert 'dataset_name' in dataset.metadata
    assert 'project_name' in dataset.metadata
    assert 'archive_date' in dataset.metadata
