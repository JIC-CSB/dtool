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

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


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
        create_archive,
    )
    from dtool.archive import compress_archive

    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    new_archive_dataset(d, no_input=True)
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

    dataset_path = new_archive_dataset(tmp_dir, no_input=True)

    expected_path = os.path.join(tmp_dir,
                                 "brassica_rnaseq_reads")
    expected_path = os.path.abspath(expected_path)
    assert dataset_path == expected_path
    assert os.path.isdir(dataset_path)

    expected_dataset_file = os.path.join(dataset_path, ".dtool-dataset")
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
    assert "unix_username" in dataset_info
    assert dataset_info["manifest_root"] == "archive"
    assert dataset_info['dataset_name'] == 'brassica_rnaseq_reads'

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


def test_new_archive_dataset_extra_content(tmp_dir):
    from dtool.arctool import new_archive_dataset

    extra_context = dict(project_name="some_project",
                         dataset_name="data_set_1")
    new_archive_dataset(tmp_dir, no_input=True, extra_context=extra_context)

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
    new_archive_dataset(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    expected_paths = [u".dtool-dataset",
                      u"README.yml",
                      u"manifest.json",
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
    from dtool.arctool import create_archive

    from dtool.arctool import new_archive_dataset, create_manifest

    new_archive_dataset(tmp_dir, no_input=True)
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
                      'brassica_rnaseq_reads/.dtool-dataset',
                      # 'brassica_rnaseq_reads/archive',
                      'brassica_rnaseq_reads/README.yml',
                      'brassica_rnaseq_reads/manifest.json',
                      'brassica_rnaseq_reads/archive/README.txt',
                      # 'brassica_rnaseq_reads/archive/dir1',
                      'brassica_rnaseq_reads/archive/file1.txt',
                      'brassica_rnaseq_reads/archive/dir1/file2.txt'])

    actual = set()
    with tarfile.open(expected_tar_filename, 'r') as tar:
        for tarinfo in tar:
            actual.add(tarinfo.path)

    assert len(expected) == len(actual)
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
    from dtool.arctool import create_archive

    from dtool.arctool import new_archive_dataset, create_manifest

    new_archive_dataset(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project + "/")

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)


def test_issue_with_log_create_archive_in_different_dir(tmp_dir):

    from dtool.arctool import create_archive

    from dtool.arctool import new_archive_dataset, create_manifest

    new_archive_dataset(tmp_dir, no_input=True)
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


def test_summarise_archive(tmp_archive):

    from dtool.arctool import summarise_archive

    summary = summarise_archive(tmp_archive)

    assert isinstance(summary, dict)

    assert summary['n_files'] == 3


def test_extract_manifest(tmp_archive):

    from dtool.arctool import extract_manifest

    extracted_manifest_path = extract_manifest(tmp_archive)

    assert os.path.isfile(extracted_manifest_path)

    with open(extracted_manifest_path) as fh:
        manifest = json.load(fh)

    assert len(manifest['file_list']) == 3


def test_extract_readme(tmp_archive):

    from dtool.arctool import extract_readme

    extracted_readme_path = extract_readme(tmp_archive)

    assert os.path.isfile(extracted_readme_path)

    with open(extracted_readme_path) as fh:
        readme = yaml.load(fh)

    assert readme['dataset_name'] == 'brassica_rnaseq_reads'


def test_create_project(tmp_dir):

    from dtool.arctool import Project
    from dtool.archive import is_collection

    expected_project_path = os.path.join(tmp_dir, 'my_test_project')

    assert not os.path.isdir(expected_project_path)

    test_project = Project(tmp_dir, 'my_test_project')

    assert test_project.path == os.path.abspath(expected_project_path)
    assert os.path.isdir(expected_project_path)
    assert is_collection(expected_project_path)

    expected_readme_path = os.path.join(expected_project_path, 'README.yml')
    assert test_project.readme_file == expected_readme_path
    assert os.path.isfile(test_project.readme_file)

    import yaml

    with open(test_project.readme_file) as fh:
        project_metadata = yaml.load(fh)

    assert project_metadata['project_name'] == 'my_test_project'

    assert test_project.metadata['project_name'] == 'my_test_project'


def test_create_project_does_not_overwrite_readme(tmp_dir):

    from dtool.arctool import Project

    test_project = Project(tmp_dir, 'my_test_project')

    readme_path = test_project.readme_file

    with open(readme_path, 'w') as fh:
        fh.write('test')

    test_project = Project(tmp_dir, 'my_test_project')

    with open(readme_path) as fh:
        readme_contents = fh.read()

    assert readme_contents == 'test'


def test_project_from_path(chdir):

    from dtool.arctool import Project

    Project('.', 'my_test_project')

    test_project = Project.from_path('my_test_project')

    assert test_project.name == 'my_test_project'
