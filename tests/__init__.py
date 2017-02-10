"""Test fixtures and utilities."""

import os
import shutil
import tempfile
import contextlib

import pytest

from dtool import DataSet

_HERE = os.path.dirname(__file__)
TEST_SAMPLE_DATASET = os.path.join(_HERE, "data", "sample_data")


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def tmp_dir_fixture(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


@pytest.fixture
def chdir_fixture(request):
    d = tempfile.mkdtemp()

    cwd = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(cwd)
        shutil.rmtree(d)


@pytest.fixture
def tmp_dataset_fixture(request):
    d = tempfile.mkdtemp()

    dataset_path = os.path.join(d, 'sample_data')
    shutil.copytree(TEST_SAMPLE_DATASET, dataset_path)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    return DataSet.from_path(dataset_path)
