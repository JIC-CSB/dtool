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


def test_descriptive_metadata_inheritence(tmp_dir):
    from dtool import Project, Collection, DataSet, DescriptiveMetadata

    project_path = tmp_dir
    project = Project("my_project")
    project.persist_to_path(project_path)

    collection_path = os.path.join(project_path, "my_collection")
    os.mkdir(collection_path)
    collection = Collection()
    collection.persist_to_path(collection_path)

    dataset_path = os.path.join(collection_path, "my_dataset")
    os.mkdir(dataset_path)
    dataset = DataSet("my_dataset")
    dataset.persist_to_path(dataset_path)

    project_metadata = DescriptiveMetadata([
        ("project_name", "my_project"),
        ("collection_name", "should_not_see_this"),
        ("dataset_name", "should_not_see_this")])
    project_metadata.persist_to_path(project_path)

    collection_metadata = DescriptiveMetadata([
        ("collection_name", "my_collection"),
        ("dataset_name", "should_not_see_this")])
    collection_metadata.persist_to_path(collection_path)

    dataset_metadata = DescriptiveMetadata([
        ("dataset_name", "my_dataset")])
    dataset_metadata.persist_to_path(dataset_path)

    dataset = DataSet.from_path(dataset_path)
    assert dataset.descriptive_metadata["project_name"] == "my_project"
    assert dataset.descriptive_metadata["collection_name"] == "my_collection"
    assert dataset.descriptive_metadata["dataset_name"] == "my_dataset"
