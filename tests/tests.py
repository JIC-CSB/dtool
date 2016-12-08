"""Tests for dtool."""

import os
import json
import shutil
import tempfile

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "output")


def test_shasum():

    from dtool import shasum

    expected = "a250369afb3eeaa96fb0df99e7755ba784dfd69c"

    test_file = os.path.join(TEST_INPUT_DATA, 'archive', 'file1.txt')
    actual = shasum(test_file)

    assert actual == expected


def test_generate_manifest():

    from dtool import generate_manifest

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

    from dtool import generate_full_file_list

    expected = ['file1.txt', 'dir1/file2.txt']

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_full_file_list(test_archive_path)

    assert sorted(actual) == sorted(expected)


def test_create_manifest():
    from dtool import create_manifest

    tmp_dir = tempfile.mkdtemp()
    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    create_manifest(os.path.join(tmp_project, "archive"))

    manifest_path = os.path.join(tmp_project, "manifest.json")
    assert os.path.isfile(manifest_path)
    shutil.rmtree(tmp_dir)


def test_create_manifest_strip_trailing_slash():
    from dtool import create_manifest

    tmp_dir = tempfile.mkdtemp()
    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    create_manifest(os.path.join(tmp_project, "archive/"))

    manifest_path = os.path.join(tmp_project, "manifest.json")
    assert os.path.isfile(manifest_path)
    shutil.rmtree(tmp_dir)
