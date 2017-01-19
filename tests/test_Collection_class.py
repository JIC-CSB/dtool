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
    expected_dtool_file = os.path.join(expected_dtool_dir, "dtool")
    assert not os.path.isdir(expected_dtool_dir)
    assert not os.path.isfile(expected_dtool_file)

    collection.persist_to_path(tmp_dir)
    assert os.path.isdir(expected_dtool_dir)
    assert os.path.isfile(expected_dtool_file)

    import json
    with open(expected_dtool_file) as fh:
        admin_metadata = json.load(fh)
    assert admin_metadata["type"] == "collection"
    assert collection.admin_metadata == admin_metadata


def test_multiple_persist_to_path_raises(tmp_dir):
    from dtool import Collection
    collection = Collection()

    collection.persist_to_path(tmp_dir)
    with pytest.raises(OSError):
        collection.persist_to_path(tmp_dir)


def test_decriptive_metadata_property(tmp_dir):
    from dtool import Collection
    collection = Collection()
    assert collection.descriptive_metadata == {}

    collection.persist_to_path(tmp_dir)
    assert collection.descriptive_metadata == {}

    with open(collection.readme_path, "w") as fh:
        fh.write("---\n")
        fh.write("project: my_project\n")
    assert collection.descriptive_metadata == {"project": "my_project"}


def test_equality():
    from copy import deepcopy
    from dtool import Collection
    collection = Collection()
    collection_again = deepcopy(collection)
    assert collection_again == collection

    # This is bonkers, don't do this!
    collection_again._uuid = "not_a_uuid"
    assert collection_again != collection
    assert collection_again.uuid == collection_again.admin_metadata["uuid"]


def test_cannot_change_uuid():
    from dtool import Collection
    collection = Collection()
    with pytest.raises(AttributeError):
        collection.uuid = "not_a_uuid"



#def test_from_path(tmp_dir):
#    from dtool import Collection
#    collection = Collection()
#    collection.persist_to_path(tmp_dir)
#
#    collection_again = Collection.from_path(tmp_dir)
#    assert collection == collection_again
