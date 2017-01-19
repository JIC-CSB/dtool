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
