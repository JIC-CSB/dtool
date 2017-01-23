"""Tests for dtool.archive.ArchiveFile class."""

import os
import json
from distutils.dir_util import copy_tree
import shutil
import tempfile
import subprocess

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


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


def test_archive_header_file_order():
    from dtool.archive import ArchiveFile
    assert ArchiveFile.header_file_order == ('.dtool/dtool',
                                             '.dtool/manifest.json',
                                             'README.yml')


def test_initialise_ArchiveFile():
    from dtool.archive import ArchiveFile
    archive = ArchiveFile()
    assert archive._tar_path is None
    assert archive._name is None
    assert archive._archive_dataset is None


# Functional tests.

def test_from_archive_directory(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFile

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(tmp_dir)

    archive_file = ArchiveFile(archive_dataset=archive_ds)
    assert archive_ds == archive_file._archive_dataset


def test_create_archive(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFile

    # Create separate directory for archive so that tarball
    # is created outside of it.
    archive_directory_path = os.path.join(tmp_dir, "input")
    os.mkdir(archive_directory_path)

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(archive_directory_path)

    # Move some data into the archive.
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(archive_directory_path, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    archive_file = ArchiveFile(archive_ds)
    tar_path = archive_file.persist_to_tar(tmp_dir)

    expected_tar_file_path = os.path.join(tmp_dir, "my_archive.tar")
    assert expected_tar_file_path == archive_file._tar_path
    assert expected_tar_file_path == tar_path

    assert os.path.isfile(expected_tar_file_path)

    # Move the original input data into a new directory.
    reference_data_path = os.path.join(tmp_dir, "expected")
    os.rename(archive_directory_path, reference_data_path)
    assert not os.path.isdir(archive_directory_path)

    # Untar the tarball just created.
    cmd = ["tar", "-xf", expected_tar_file_path]
    subprocess.check_call(cmd, cwd=tmp_dir)

    # Test that the archive has been re-instated by untaring.
    assert os.path.isdir(archive_directory_path)

    # Test order of files in tarball.

    cmd = ["tar", "-tf", expected_tar_file_path]
    output = subprocess.check_output(cmd)

    split_output = output.split()

    expected_first_header_file = os.path.join(
        'input',
        ArchiveFile.header_file_order[0])

    assert split_output[0].decode("utf-8") == expected_first_header_file

    for n, filename in enumerate(ArchiveFile.header_file_order):
        expected_filename = os.path.join('input', filename)
        assert split_output[n].decode("utf-8") == expected_filename

    from dtool import generate_relative_paths
    untarred_file_set = set(generate_relative_paths(archive_directory_path))
    reference_file_set = set(generate_relative_paths(reference_data_path))
    assert untarred_file_set == reference_file_set

    # Test correctness of manifest

    manifest_path = os.path.join(
        archive_directory_path, '.dtool', 'manifest.json')
    with open(manifest_path) as fh:
        manifest = json.load(fh)

    assert len(manifest['file_list']) == 2


def test_from_tar(tmp_archive):
    from dtool.archive import ArchiveFile

    unzip_command = ["gunzip", tmp_archive]
    subprocess.call(unzip_command)

    tar_filename, _ = tmp_archive.rsplit('.', 1)

    archive_file = ArchiveFile.from_file(tar_filename)

    assert isinstance(archive_file, ArchiveFile)
    assert archive_file._tar_path == tar_filename

    assert 'dtool_version' in archive_file.admin_metadata
    assert archive_file.admin_metadata['name'] == 'brassica_rnaseq_reads'
    assert len(archive_file.admin_metadata['uuid']) == 36
    assert 'file_list' in archive_file.manifest


def test_from_tar_gz(tmp_archive):
    from dtool.archive import ArchiveFile

    archive_file = ArchiveFile.from_file(tmp_archive)

    assert isinstance(archive_file, ArchiveFile)
    assert archive_file._tar_path == tmp_archive

    assert 'dtool_version' in archive_file.admin_metadata
    assert archive_file.admin_metadata['name'] == 'brassica_rnaseq_reads'
    assert len(archive_file.admin_metadata['uuid']) == 36
    assert 'file_list' in archive_file.manifest

def test_archive_calculate_hash(tmp_archive):
    from dtool.archive import ArchiveFile

    archive = ArchiveFile.from_file(tmp_archive)

    actual = archive.calculate_file_hash('file1.txt')
    expected = 'a250369afb3eeaa96fb0df99e7755ba784dfd69c'

    assert actual == expected
