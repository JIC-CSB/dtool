"""Test the archive module."""

import os
import json
from distutils.dir_util import copy_tree
import tempfile
import shutil
import subprocess

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")
TEST_DESCRIPTIVE_METADATA = dict([
        ("project_name", u"my_project"),
        ("dataset_name", u"brassica_rnaseq_reads"),
        ("confidential", False),
        ("personally_identifiable_information", False),
        ("owner_name", u"Your Name"),
        ("owner_email", u"your.email@example.com"),
        ("unix_username", u"namey"),
        ("archive_date", u"2017-01-01"),
    ])


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


@pytest.fixture
def tmp_archive(request):

    from dtool.archive import (
        ArchiveDataSet,
        ArchiveFile)

    from dtool.archive import compress_archive

    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    archive_directory_path = os.path.join(d, "brassica_rnaseq_reads")
    os.mkdir(archive_directory_path)
    archive_ds = ArchiveDataSet("brassica_rnaseq_reads")
    archive_ds.persist_to_path(archive_directory_path)

    # Move some data into the archive.
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(archive_directory_path, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    archive_file = ArchiveFile(archive_ds)
    tar_path = archive_file.persist_to_tar(d)
    compress_archive(tar_path)

    return tar_path + '.gz'


def test_compress_archive(tmp_archive):

    from dtool.archive import compress_archive

    tar_filename, _ = tmp_archive.rsplit('.', 1)
    expected_gz_filename = tar_filename + '.gz'
    expected_gz_filename = os.path.abspath(expected_gz_filename)

    unzip_command = ["gunzip", tmp_archive]
    subprocess.call(unzip_command)
    assert os.path.isfile(tar_filename)
    assert not os.path.isfile(expected_gz_filename)

    gzip_filename = compress_archive(tar_filename)

    assert gzip_filename == expected_gz_filename
    assert os.path.isfile(expected_gz_filename)
    assert not os.path.isfile(tar_filename)


def test_extract_file(tmp_archive):
    from dtool.archive import extract_file

    base_dir, tar_gz_filename = os.path.split(tmp_archive)
    file_prefix, ext = tar_gz_filename.split(".", 1)

    expected_path = os.path.join(base_dir,
                                 file_prefix,
                                 "README.yml")
    expected_path = os.path.abspath(expected_path)
    readme_path = extract_file(tmp_archive, "README.yml")
    assert readme_path == expected_path
    assert os.path.isfile(readme_path)

    # Remove the extracted file and unzip the tarball.
    os.unlink(readme_path)
    unzip_command = ["gunzip", tmp_archive]
    subprocess.call(unzip_command)
    tarball_path, _ = tmp_archive.rsplit(".", 1)
    assert os.path.isfile(tarball_path)

    # Test that the extract_file method works on unzipped tarballs too.
    readme_path = extract_file(tarball_path, "README.yml")
    assert readme_path == expected_path
    assert os.path.isfile(readme_path)


def test_archive_verify_all(tmp_archive):
    from dtool.archive import verify_all

    assert verify_all(tmp_archive)


def test_verify_file(tmp_archive):
    from dtool.archive import verify_file

    assert verify_file(tmp_archive, 'file1.txt')


def test_icreate_collection(tmp_dir):
    from dtool.archive import icreate_collection

    expected_path = os.path.join(tmp_dir, 'test_collection')

    assert not os.path.isdir(expected_path)

    collection_path = icreate_collection(tmp_dir, 'test_collection')

    assert expected_path == collection_path
    assert os.path.isdir(collection_path)

    collection_file_path = os.path.join(collection_path, '.dtool-collection')

    with open(collection_file_path) as fh:
        collection_info = json.load(fh)

    original_uuid = collection_info['uuid']
    assert len(original_uuid) == 36

    # Check that function is idempotent
    collection_path = icreate_collection(tmp_dir, 'test_collection')

    with open(collection_file_path) as fh:
        collection_info = json.load(fh)

    assert collection_info['uuid'] == original_uuid


def test_icreate_raises_valueerror_when_run_on_existing_dir_with_no_collection_file(tmp_dir):  # NOQA
    from dtool.archive import icreate_collection

    empty_path = os.path.join(tmp_dir, 'test_collection')
    os.mkdir(empty_path)

    with pytest.raises(ValueError) as excinfo:
        icreate_collection(tmp_dir, 'test_collection')

    assert 'Path exists but is not a collection' in str(excinfo.value)


def test_is_collection(tmp_dir):
    from dtool.archive import is_collection, icreate_collection

    assert is_collection(tmp_dir) is False

    icreate_collection(tmp_dir, 'my_collection')

    assert is_collection(os.path.join(tmp_dir, 'my_collection'))
