"""Test the dtool.Collection class."""

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


def test_Collection_initialisation():
    from dtool import Collection
    collection = Collection()
    assert len(collection.uuid) == 36
    assert collection.abs_readme_path is None
    assert collection._admin_metadata["type"] == "collection"
    assert isinstance(collection.dtool_version, str)


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
    assert collection._admin_metadata == admin_metadata


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

    with open(collection.abs_readme_path, "w") as fh:
        fh.write("---\n")
        fh.write("project: my_project\n")
    assert collection.descriptive_metadata == {"project": "my_project"}


def test_equality():
    from copy import deepcopy
    from dtool import Collection
    collection = Collection()
    collection_again = deepcopy(collection)
    assert collection_again == collection


def test_cannot_change_uuid():
    from dtool import Collection
    collection = Collection()
    with pytest.raises(AttributeError):
        collection.uuid = "not_a_uuid"


def test_from_path(tmp_dir):
    from dtool import Collection
    collection = Collection()
    collection.persist_to_path(tmp_dir)

    collection_again = Collection.from_path(tmp_dir)
    assert collection == collection_again


def test_check_type_on_from_path(chdir):
    from dtool import Collection

    admin_metadata = {'type': 'dataset'}
    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)
    dtool_file = os.path.join(dtool_dir, 'dtool')

    with open(dtool_file, 'w') as fh:
        json.dump(admin_metadata, fh)

    with pytest.raises(ValueError):
        Collection.from_path('.')


def test_from_path_raises_valuerror_if_type_does_not_exist(chdir):
    from dtool import Collection

    admin_metadata = {}
    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)
    dtool_file = os.path.join(dtool_dir, 'dtool')

    with open(dtool_file, 'w') as fh:
        json.dump(admin_metadata, fh)

    with pytest.raises(ValueError):
        Collection.from_path('.')


def test_no_dtool_file_raises_valueerror(chdir):
    from dtool import Collection

    dtool_dir = '.dtool'
    os.mkdir(dtool_dir)

    with pytest.raises(ValueError):
        Collection.from_path('.')


def test_no_dtool_dir_raises_valueerror(tmp_dir):
    from dtool import Collection

    with pytest.raises(ValueError):
        Collection.from_path(tmp_dir)


def test_persist_to_path_sets_abs_readme_path(tmp_dir):
    from dtool import Collection

    collection = Collection()

    expected_abs_readme_path = os.path.join(tmp_dir, 'README.yml')

    assert collection.abs_readme_path is None

    collection.persist_to_path(tmp_dir)

    assert collection.abs_readme_path == expected_abs_readme_path
