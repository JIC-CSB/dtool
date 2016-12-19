"""Test the archive module."""

import os
import tarfile
from distutils.dir_util import copy_tree
import contextlib
import tempfile
import shutil

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


@contextlib.contextmanager
def remember_cwd():
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_create_archive(tmp_dir):
    from dtool.archive import create_archive

    from dtool import new_archive
    from dtool.manifest import create_manifest

    new_archive(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project)

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)

    # Test that all expected files are present in archive
    expected = set(['brassica_rnaseq_reads',
                    'brassica_rnaseq_reads/.dtool-dataset',
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

    # Test that order of critical files is correct
    expected = ['brassica_rnaseq_reads/.dtool-dataset',
                'brassica_rnaseq_reads/README.yml',
                'brassica_rnaseq_reads/manifest.json']

    actual = []
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.append(tarinfo.path)

    for e, a in zip(expected, actual):
        assert e == a


def test_create_archive_with_trailing_slash(tmp_dir):
    from dtool.archive import create_archive

    from dtool import new_archive
    from dtool.manifest import create_manifest

    new_archive(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project + "/")

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)


def test_issue_with_log_create_archive_in_different_dir(tmp_dir):

    from dtool.archive import create_archive

    from dtool import new_archive
    from dtool.manifest import create_manifest

    new_archive(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    with remember_cwd():
        os.chdir(tmp_project)
        actual_tar_path = create_archive(tmp_project)

    expected_tar_path = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')

    assert expected_tar_path == actual_tar_path


#############################################################################
# Test archive compress functions.
#############################################################################

def test_compress_archive(tmp_dir):

    from dtool.archive import create_archive, compress_archive

    from dtool import new_archive
    from dtool.manifest import create_manifest

    new_archive(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    tar_filename = create_archive(tmp_project)
    assert os.path.isfile(tar_filename)

    gzip_filename = compress_archive(tar_filename)

    expected_gz_filename = tar_filename + '.gz'
    expected_gz_filename = os.path.abspath(expected_gz_filename)
    assert gzip_filename == expected_gz_filename
    assert os.path.isfile(expected_gz_filename)
    assert not os.path.isfile(tar_filename)
