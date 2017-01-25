"""Tests for dtool.archive.ArchiveFile class."""

import os
from distutils.dir_util import copy_tree
import shutil
import tempfile
import subprocess
import contextlib

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


@contextlib.contextmanager
def get_context_tmp_dir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d)


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
        ArchiveFileBuilder)

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

    archive_builder = ArchiveFileBuilder.from_path(archive_directory_path)
    tar_path = archive_builder.persist_to_tar(d)
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


# Functional tests.


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


# def test_extract_readme(tmp_archive):
#    from dtool.archive import ArchiveFile
#    archive = ArchiveFile.from_file(tmp_archive)
#    with get_context_tmp_dir() as d:
#        archive.extract_file(".dtool/manifest.json", d)
#        expected_path = os.path.join(
#           d, archive._name, ".dtool", "manifest.json")
#        assert os.path.isfile(expected_path)
