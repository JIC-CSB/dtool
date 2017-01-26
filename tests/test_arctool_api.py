"""Test the archtool module api."""

import os
import json
import contextlib
import shutil
import tempfile
from distutils.dir_util import copy_tree
import tarfile

import yaml
import magic
import pytest

from dtool.archive import ArchiveFileBuilder

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


def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

    archive_builder = ArchiveFileBuilder.from_path(path)
    output_path = os.path.join(path, "..")
    return archive_builder.persist_to_tar(output_path)


@pytest.fixture
def chdir(request):
    d = tempfile.mkdtemp()

    cwd = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(cwd)
        shutil.rmtree(d)


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


@pytest.fixture
def tmp_archive(request):

    from dtool.arctool import (
        new_archive_dataset,
        create_manifest,
    )
    from dtool.archive import compress_archive

    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    new_archive_dataset(d, TEST_DESCRIPTIVE_METADATA)
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


def test_archive_fixture(tmp_archive):

    mimetype = magic.from_file(tmp_archive, mime=True)

    assert mimetype == 'application/x-gzip'


def test_new_archive_dataset(tmp_dir):
    from dtool.arctool import new_archive_dataset

    dataset, dataset_path, _ = new_archive_dataset(tmp_dir,
                                                   TEST_DESCRIPTIVE_METADATA)

    expected_path = os.path.join(tmp_dir,
                                 "brassica_rnaseq_reads")
    expected_path = os.path.abspath(expected_path)
    assert dataset_path == expected_path
    assert os.path.isdir(dataset_path)

    expected_dataset_file = os.path.join(dataset_path, ".dtool", "dtool")
    assert os.path.isfile(expected_dataset_file)

    readme_yml_path = os.path.join(tmp_dir,
                                   "brassica_rnaseq_reads",
                                   "README.yml")
    assert os.path.isfile(readme_yml_path)

    readme_txt_path = os.path.join(tmp_dir,
                                   "brassica_rnaseq_reads",
                                   "archive",
                                   "README.txt")
    assert os.path.isfile(readme_txt_path)

    # Test that .dtool-dataset file is valid
    with open(expected_dataset_file, 'r') as fh:
        dataset_info = json.load(fh)

    assert "dtool_version" in dataset_info
    assert "uuid" in dataset_info
    assert "creator_username" in dataset_info
    assert dataset_info["manifest_root"] == "archive"
    assert dataset_info['name'] == 'brassica_rnaseq_reads'

    # Test that yaml is valid.
    with open(readme_yml_path, "r") as fh:
        readme_data = yaml.load(fh)
    assert readme_data["dataset_name"] == "brassica_rnaseq_reads"

    # Also assert that confidential and personally_identifiable_information
    # are set to False by default.
    assert not readme_data["confidential"]
    assert not readme_data["personally_identifiable_information"]


def test_readme_yml_is_valid(mocker):
    from dtool.arctool import readme_yml_is_valid
    # Not that the log function get imported into the dtool.arctool namespace
    from dtool.arctool import log  # NOQA

    patched_log = mocker.patch("dtool.arctool.log")

    assert not readme_yml_is_valid("")
    patched_log.assert_called_with("README.yml invalid: empty file")

    # This should be ok.
    assert readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
archive_date: 2016-01-12
""")

    # Missing a project name.
    assert not readme_yml_is_valid("""---
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
archive_date: 2016-01-12
""")
    patched_log.assert_called_with("README.yml is missing: project_name")

    # Invalid date.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners: NA
archive_date: some day
""")
    patched_log.assert_called_with(
        "README.yml invalid: archive_date is not a date")

    # Owners is not a list.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners: NA
archive_date: 2016-01-12
""")
    patched_log.assert_called_with("README.yml invalid: owners is not a list")

    # An owner needs a name.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
  - email: twos@example.com
archive_date: 2016-01-12
""")
    patched_log.assert_called_with(
        "README.yml invalid: owner is missing a name")

    # An owner needs an email.
    assert not readme_yml_is_valid("""---
project_name: some_project
dataset_name: data_set_1
confidential: False
personally_identifiable_information: False
owners:
  - name: Some One
    email: ones@example.com
  - name: Another Two
archive_date: 2016-01-12
""")
    patched_log.assert_called_with(
        "README.yml invalid: owner is missing an email")


def test_new_archive_dataset_input_descriptive_metadata(tmp_dir):
    from dtool.arctool import new_archive_dataset

    metadata = dict(project_name="some_project",
                    dataset_name="data_set_1")
    new_archive_dataset(tmp_dir, metadata)

    # Test file creation.
    readme_yml_path = os.path.join(tmp_dir,
                                   "data_set_1",
                                   "README.yml")
    assert os.path.isfile(readme_yml_path)

    # Test that yaml is valid.
    with open(readme_yml_path, "r") as fh:
        readme_data = yaml.load(fh)
    assert readme_data["project_name"] == "some_project"
    assert readme_data["dataset_name"] == "data_set_1"


def test_rel_paths_for_archiving(tmp_dir):
    from dtool.arctool import rel_paths_for_archiving

    from dtool.arctool import new_archive_dataset, create_manifest
    new_archive_dataset(tmp_dir, TEST_DESCRIPTIVE_METADATA)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    expected_paths = [u".dtool/dtool",
                      u".dtool/manifest.json",
                      u"README.yml",
                      u"archive/README.txt",
                      u"archive/file1.txt",
                      u"archive/dir1/file2.txt"]
    actual_paths, actual_size = rel_paths_for_archiving(tmp_project)

    expected_size = 0
    for p in expected_paths:
        ap = os.path.join(tmp_project, p)
        expected_size = expected_size + os.stat(ap).st_size
    assert actual_size == expected_size

    # Ensure that the first free files are in fixed order.
    for i in range(3):
        assert actual_paths[i] == expected_paths[i]

    # Assert that all files exist.
    assert len(actual_paths) == len(expected_paths)
    assert set(actual_paths) == set(expected_paths)


def test_create_archive(tmp_dir):
    from dtool.arctool import new_archive_dataset, create_manifest

    new_archive_dataset(tmp_dir, TEST_DESCRIPTIVE_METADATA)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project)

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)

    # Test that all expected files are present in archive
    expected = set([  # 'brassica_rnaseq_reads',
                      'brassica_rnaseq_reads/.dtool/dtool',
                      'brassica_rnaseq_reads/.dtool/manifest.json',
                      'brassica_rnaseq_reads/archive',
                      'brassica_rnaseq_reads/README.yml',
                      'brassica_rnaseq_reads/archive/README.txt',
                      'brassica_rnaseq_reads/archive/dir1',
                      'brassica_rnaseq_reads/archive/file1.txt',
                      'brassica_rnaseq_reads/archive/dir1/file2.txt'])

    actual = set()
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.add(tarinfo.path)

    assert len(expected) == len(actual)
    assert expected == actual, (expected, actual)

    # Test that order of critical files is correct
    expected = ['brassica_rnaseq_reads/.dtool/dtool',
                'brassica_rnaseq_reads/.dtool/manifest.json',
                'brassica_rnaseq_reads/README.yml',
                ]

    actual = []
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.append(tarinfo.path)

    for e, a in zip(expected, actual):
        assert e == a


def test_create_archive_with_trailing_slash(tmp_dir):
    from dtool.arctool import new_archive_dataset, create_manifest

    new_archive_dataset(tmp_dir, TEST_DESCRIPTIVE_METADATA)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project + "/")

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)


def test_issue_with_log_create_archive_in_different_dir(tmp_dir):
    from dtool.arctool import new_archive_dataset, create_manifest

    new_archive_dataset(tmp_dir, TEST_DESCRIPTIVE_METADATA)
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
