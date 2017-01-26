"""Test the manifest module."""

import os
import json
import shutil
import tempfile

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "basic", "output")
TEST_MIMETYPE_DATA = os.path.join(HERE, "data", "mimetype", "input")


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_file_metadata():
    from dtool.manifest import file_metadata
    png_path = os.path.join(TEST_MIMETYPE_DATA,
                            "archive",
                            "tiny.png")
    metadata = file_metadata(png_path)
    expected_keys = ["hash", "size", "mtime", "mimetype"]
    assert set(expected_keys) == set(metadata.keys())
    assert metadata["hash"] == "09648d19e11f0b20e5473594fc278afbede3c9a4"
    assert metadata["size"] == 276
    assert metadata["mimetype"] == "image/png"


def test_generate_manifest():

    from dtool.manifest import generate_manifest

    expected_manifest_file = os.path.join(TEST_OUTPUT_DATA, 'manifest.json')
    with open(expected_manifest_file) as fh:
        expected = json.load(fh)

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_manifest(test_archive_path)

    for a, e in zip(actual["file_list"], expected["file_list"]):
        assert a["path"] == e["path"]
        assert a["hash"] == e["hash"]
        assert a["size"] == e["size"]


def test_generate_relative_paths():

    from dtool.manifest import generate_relative_paths

    expected = ['file1.txt', 'dir1/file2.txt']

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_relative_paths(test_archive_path)

    assert sorted(actual) == sorted(expected)


def test_generate_relative_paths_with_trailing_slash():

    from dtool.manifest import generate_relative_paths

    expected = ['file1.txt', 'dir1/file2.txt']

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    test_archive_path = test_archive_path + "/"
    actual = generate_relative_paths(test_archive_path)

    assert sorted(actual) == sorted(expected)


def test_generate_manifest(tmp_dir):
    from dtool import generate_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    archive_subdir_path = os.path.join(tmp_project, "archive")
    manifest = generate_manifest(archive_subdir_path)

    assert "file_list" in manifest

    file_list = manifest["file_list"]
    file_dict_by_path = {entry['path']: entry for entry in file_list}

    assert "file1.txt" in file_dict_by_path

    file1_entry = file_dict_by_path["file1.txt"]

    assert file1_entry["mimetype"] == "text/plain"
    assert "hash_function" in manifest
    assert "dtool_version" in manifest


def test_manifest_mimetypes(tmp_dir):
    from dtool import generate_manifest

    tmp_project = os.path.join(tmp_dir, "proj")
    shutil.copytree(TEST_MIMETYPE_DATA, tmp_project)

    archive_subdir_path = os.path.join(tmp_project, "archive")
    manifest = generate_manifest(archive_subdir_path)

    file_list = manifest["file_list"]

    expected_mimetypes = {
        'actually_a_png.txt': 'image/png',
        'actually_a_text_file.jpg': 'text/plain',
        'empty_file': 'inode/x-empty',
        'random_bytes': 'application/octet-stream',
        'real_text_file.txt': 'text/plain',
        'tiny.png': 'image/png'
    }

    for file in file_list:
        file_path = file['path']
        actual = file['mimetype']
        expected = expected_mimetypes[file_path]
        assert expected == actual


def test_generate_filedict_list():
    from dtool.manifest import generate_filedict_list

    relative_paths = ['myfile.txt',
                      'anotherfile.txt',
                      'adir/afile.txt',
                      'long/path/separator/file.txt']

    actual = generate_filedict_list(relative_paths)

    expected = [{'path': 'myfile.txt'},
                {'path': 'anotherfile.txt'},
                {'path': 'adir/afile.txt'},
                {'path': 'long/path/separator/file.txt'}]

    assert expected == actual


def test_create_filedict_manifest(tmp_dir):
    from dtool.manifest import create_filedict_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)

    filedict_manifest = create_filedict_manifest(
        os.path.join(tmp_project, "archive/"))

    assert len(filedict_manifest) == 2

    file_dict_by_path = {entry['path']: entry for entry in filedict_manifest}

    assert "file1.txt" in file_dict_by_path

    file1_entry = file_dict_by_path["file1.txt"]

    assert file1_entry["size"] == 17
