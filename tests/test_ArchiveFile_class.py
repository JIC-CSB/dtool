"""Tests for dtool.archive.ArchiveFile class."""

import os
import shutil
import tempfile
import subprocess

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

    assert os.path.isfile(expected_tar_path)

    # Move the original input data into a new directory.
    reference_data_path = os.path.join(tmp_dir, "expected")
    os.rename(archive_directory_path, reference_data_path)
    assert not os.path.isdir(expected_tar_path)

    # Untar the tarball just created.
    cmd = ["tar", "-xf", expected_tar_path]
    subprocess.check_call(cmd)

    assert os.path.isdir(reference_data_path)

    cmd = ["tar", "-tf", expected_tar_path]
    output = subprocess.check_output(cmd)

    split_output = output.split()

    expected_first_header_file = os.path.join(
        'input',
        ArchiveFile.header_file_order[0])

    assert split_output[0] == expected_first_header_file

    for n, filename in enumerate(ArchiveFile.header_file_order):
        expected_filename = os.path.join('input', filename)
        assert split_output[n] == expected_filename

#    from filecmp import dircmp
#    dcmp = dircmp(e
