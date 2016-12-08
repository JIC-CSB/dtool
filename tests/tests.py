"""Tests for dtool."""

import os
import json
import shutil
import tarfile
import tempfile
from distutils.dir_util import copy_tree

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "output")


def test_split_safe_path():
    from dtool import split_safe_path
    assert split_safe_path("/") == "/"
    assert split_safe_path("/root") == "/root"
    assert split_safe_path("/root/") == "/root"


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


def test_new_archive():
    from dtool import new_archive

    tmp_dir = tempfile.mkdtemp()
    new_archive(tmp_dir, no_input=True)

    readme_yml_path = os.path.join(tmp_dir,
                                   "brassica_rnaseq_reads",
                                   "README.yml")
    assert os.path.isfile(readme_yml_path)

    readme_txt_path = os.path.join(tmp_dir,
                                   "brassica_rnaseq_reads",
                                   "archive",
                                   "README.txt")
    assert os.path.isfile(readme_txt_path)

    shutil.rmtree(tmp_dir)


def test_create_archive():
    from dtool import create_archive, create_manifest, new_archive

    tmp_dir = tempfile.mkdtemp()
    new_archive(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project)

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)

    expected = set(['brassica_rnaseq_reads',
                    'brassica_rnaseq_reads/archive',
                    'brassica_rnaseq_reads/README.yml',
                    'brassica_rnaseq_reads/manifest.json',
                    'brassica_rnaseq_reads/archive/README.txt',
                    'brassica_rnaseq_reads/archive/dir1',
                    'brassica_rnaseq_reads/archive/file1.txt',
                    'brassica_rnaseq_reads/archive/dir1/file2.txt'])

    actual = set()
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.add(tarinfo.path)

    assert expected == actual, (expected, actual)

    shutil.rmtree(tmp_dir)
