"""Test the archive module."""

import os
from distutils.dir_util import copy_tree
import tempfile
import shutil
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

    from dtool.arctool import new_archive, create_manifest, create_archive
    from dtool.archive import compress_archive

    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    new_archive(d, no_input=True)
    tmp_project = os.path.join(d, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project)
    compress_archive(tmp_project + '.tar')

    archive_name = tmp_project + '.tar' + '.gz'

    shutil.rmtree(archive_output_path)

    return archive_name


def test_initialise_and_append_to_tar_archive(tmp_dir):
    from dtool.archive import initialise_tar_archive, append_to_tar_archive
    tmp_project = os.path.join(tmp_dir, "project")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    expected_path = os.path.join(tmp_dir, "project.tar")
    actual_path = initialise_tar_archive(tmp_project,
                                         "archive/file1.txt")
    assert actual_path == expected_path
    assert os.path.isfile(expected_path)

    actual_path = append_to_tar_archive(tmp_project,
                                        "archive/dir1/file2.txt")
    assert actual_path == expected_path
    assert os.path.isfile(expected_path)


def test_compress_archive(tmp_dir):

    from dtool.archive import compress_archive

    from dtool.arctool import new_archive, create_manifest, create_archive

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


def test_archive_from_file(tmp_archive):
    from dtool.archive import Archive

    archive = Archive.from_file(tmp_archive)

    assert archive.name == 'brassica_rnaseq_reads'
    assert len(archive.uuid) == 36
    assert archive.info['dataset_name'] == 'brassica_rnaseq_reads'
