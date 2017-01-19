"""Test the dtool.Collection class."""

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


def test_Collection_initialisation():
    from dtool import Collection
    collection = Collection()
    assert len(collection.uuid) == 36


def test_persist_to_path(tmp_dir):
    from dtool import Collection
    collection = Collection()

    expected_dtool_dir = os.path.join(tmp_dir, ".dtool")
    assert not os.path.isdir(expected_dtool_dir)

    collection.persist_to_path(tmp_dir)

    assert os.path.isdir(expected_dtool_dir)
