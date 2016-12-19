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


def test_generate_full_file_list():

    from dtool.manifest import generate_full_file_list

    expected = ['file1.txt', 'dir1/file2.txt']

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_full_file_list(test_archive_path)

    assert sorted(actual) == sorted(expected)


def test_generate_full_file_list_with_trailing_slash():

    from dtool.manifest import generate_full_file_list

    expected = ['file1.txt', 'dir1/file2.txt']

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    test_archive_path = test_archive_path + "/"
    actual = generate_full_file_list(test_archive_path)

    assert sorted(actual) == sorted(expected)


def test_create_manifest(tmp_dir):
    from dtool.manifest import create_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    manifest_path = create_manifest(os.path.join(tmp_project, "archive"))

    expected_path = os.path.join(tmp_project, "manifest.json")
    expected_path = os.path.abspath(expected_path)
    assert manifest_path == expected_path
    assert os.path.isfile(manifest_path)

    # Ensure manifest is valid json.
    with open(manifest_path, "r") as fh:
        manifest = json.load(fh)

    assert "file_list" in manifest

    file_list = manifest["file_list"]
    file_dict_by_path = {entry['path']: entry for entry in file_list}

    assert "file1.txt" in file_dict_by_path

    file1_entry = file_dict_by_path["file1.txt"]

    assert file1_entry["mimetype"] == "text/plain"
    assert "hash_function" in manifest
    assert "dtool_version" in manifest


def test_manifest_mimetypes(tmp_dir):
    from dtool.manifest import create_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_MIMETYPE_DATA, tmp_project)
    create_manifest(os.path.join(tmp_project, "archive"))

    manifest_path = os.path.join(tmp_project, "manifest.json")
    assert os.path.isfile(manifest_path)

    # Ensure manifest is valid json.
    with open(manifest_path, "r") as fh:
        manifest = json.load(fh)

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


def test_create_manifest_strip_trailing_slash(tmp_dir):
    from dtool.manifest import create_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    create_manifest(os.path.join(tmp_project, "archive/"))

    manifest_path = os.path.join(tmp_project, "manifest.json")
    assert os.path.isfile(manifest_path)