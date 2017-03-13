"""Tests for the _DtoolObject base class."""

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


def test_parent_property():
    from dtool import _DtoolObject
    dtool_object = _DtoolObject()
    assert dtool_object._filesystem_parent is None


####################
# Functional tests
####################


def test_from_path_on_collection(tmp_dir):
    from dtool import _DtoolObject, Collection

    collection = Collection()
    collection.persist_to_path(tmp_dir)

    dtool_object = _DtoolObject.from_path(tmp_dir)
    assert dtool_object._abs_path == tmp_dir
    assert dtool_object.uuid == collection.uuid


def test_from_path_on_empty_dir_raises_NotDtoolObject(tmp_dir):
    from dtool import _DtoolObject, NotDtoolObject
    with pytest.raises(NotDtoolObject):
        _DtoolObject.from_path(tmp_dir)
