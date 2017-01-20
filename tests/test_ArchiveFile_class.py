"""Tests for dtool.archive.ArchiveFile class."""

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


def test_archive_header_file_order():
    from dtool.archive import ArchiveFile
    assert ArchiveFile.header_file_order == ('.dtool/dtool',
                                             '.dtool/manifest.json',
                                             'README.yml')


def test_initialise_ArchiveFile():
    from dtool.archive import ArchiveFile
    archive = ArchiveFile()
    assert archive._tar_path is None


# Functional tests.

def test_from_archive_directory(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFile

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(tmp_dir)

    archive_file = ArchiveFile(archive_dataset=archive_ds)
    assert archive_ds == archive_file.archive_dataset


def test_create_archive(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFile

    # Create separate directory for archive so that tarball
    # is created outside of it.
    archive_directory_path = os.path.join(tmp_dir, "input")
    os.mkdir(archive_directory_path)

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(archive_directory_path)

    archive_file = ArchiveFile(archive_ds)
    tar_path = archive_file.persist_to_tar(tmp_dir)

    expected_tar_path = os.path.join(tmp_dir, "my_archive.tar")
    assert expected_tar_path == archive_file._tar_path
    assert expected_tar_path == tar_path
