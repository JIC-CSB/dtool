"""Tests for dtool."""

import os
import json
import shutil
import tarfile
import tempfile
import subprocess
from distutils.dir_util import copy_tree

import yaml
import magic
import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "basic", "output")
TEST_MIMETYPE_DATA = os.path.join(HERE, "data", "mimetype", "input")


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


@pytest.fixture
def tmp_archive(request):

    from dtool import (
        compress_archive,
        create_archive,
        create_manifest,
        new_archive
        )

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


def test_split_safe_path():
    from dtool import split_safe_path
    assert split_safe_path("/") == "/"
    assert split_safe_path("/root") == "/root"
    assert split_safe_path("/root/") == "/root"


def test_version_is_str():
    from dtool import __version__
    assert isinstance(__version__, str)


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


def test_create_manifest(tmp_dir):
    from dtool import create_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    create_manifest(os.path.join(tmp_project, "archive"))

    manifest_path = os.path.join(tmp_project, "manifest.json")
    assert os.path.isfile(manifest_path)

    # Ensure manifest is valid json.
    with open(manifest_path, "r") as fh:
        manifest = json.load(fh)

    # Make sure that the "arctool_version" is in the generated manifest.
    assert "arctool_version" in manifest


def test_create_manifest_strip_trailing_slash(tmp_dir):
    from dtool import create_manifest

    tmp_project = os.path.join(tmp_dir, "proj")

    shutil.copytree(TEST_INPUT_DATA, tmp_project)
    create_manifest(os.path.join(tmp_project, "archive/"))

    manifest_path = os.path.join(tmp_project, "manifest.json")
    assert os.path.isfile(manifest_path)


def test_new_archive(tmp_dir):
    from dtool import new_archive

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

    # Test that yaml is valid.
    with open(readme_yml_path, "r") as fh:
        readme_data = yaml.load(fh)
    assert readme_data["dataset_name"] == "brassica_rnaseq_reads"

    # Also test that the README.yml file has a "arctool_version" key.
    assert "arctool_version" in readme_data

    # Also assert that confidential and personally_identifiable_information
    # are set to False by default.
    assert not readme_data["confidential"]
    assert not readme_data["personally_identifiable_information"]


def test_readme_yml_is_valid(mocker):
    from dtool import readme_yml_is_valid
    from dtool import log  # NOQA

    patched_log = mocker.patch("dtool.log")

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


def test_new_archive_extra_content(tmp_dir):
    from dtool import new_archive

    extra_context = dict(project_name="some_project",
                         dataset_name="data_set_1")
    new_archive(tmp_dir, no_input=True, extra_context=extra_context)

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


def test_create_archive(tmp_dir):
    from dtool import create_archive, create_manifest, new_archive

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


def test_compress_archive(tmp_dir):

    from dtool import create_archive, create_manifest, new_archive

    from dtool import compress_archive

    new_archive(tmp_dir, no_input=True)
    tmp_project = os.path.join(tmp_dir, "brassica_rnaseq_reads")
    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(tmp_project, 'archive')
    copy_tree(archive_input_path, archive_output_path)
    create_manifest(os.path.join(tmp_project, "archive/"))

    create_archive(tmp_project)

    expected_tar_filename = os.path.join(tmp_dir, 'brassica_rnaseq_reads.tar')
    assert os.path.isfile(expected_tar_filename)

    compress_archive(expected_tar_filename)

    expected_gz_filename = expected_tar_filename + '.gz'
    assert os.path.isfile(expected_gz_filename)
    assert not os.path.isfile(expected_tar_filename)


def test_generate_slurm_submission_script():

    from dtool import generate_slurm_script

    job_parameters = {'n_cores': 8, 'partition': 'rg-sv'}
    command_string = "arctool archive compress -c 8 /tmp/staging/mytar.tar"
    actual_script = generate_slurm_script(command_string,
                                          job_parameters)

    actual = actual_script.split('\n')[-1]

    expected = 'arctool archive compress -c 8 /tmp/staging/mytar.tar'

    assert expected == actual, (expected, actual)


def test_archive_fixture(tmp_archive):

    mimetype = magic.from_file(tmp_archive, mime=True)

    assert mimetype == 'application/x-gzip'


def test_summarise_archive(tmp_archive):

    from dtool import summarise_archive

    summary = summarise_archive(tmp_archive)

    assert isinstance(summary, dict)

    assert summary['n_files'] == 3


def test_extract_file(tmp_archive):
    from dtool import extract_file
    extracted_path = extract_file(tmp_archive, "README.yml")
    assert os.path.isfile(extracted_path)

    # Remove the extracted file and unzip the tarball.
    os.unlink(extracted_path)
    unzip_command = ["gunzip", tmp_archive]
    subprocess.call(unzip_command)
    tarball_path, _ = tmp_archive.rsplit(".", 1)
    assert os.path.isfile(tarball_path)

    # Test that the extract_file method works on unzipped tarballs too.
    extracted_path = extract_file(tarball_path, "README.yml")
    assert os.path.isfile(extracted_path)


def test_extract_manifest(tmp_archive):

    from dtool import extract_manifest

    extracted_manifest_path = extract_manifest(tmp_archive)

    assert os.path.isfile(extracted_manifest_path)

    with open(extracted_manifest_path) as fh:
        manifest = json.load(fh)

    assert len(manifest['file_list']) == 3


def test_extract_readme(tmp_archive):

    from dtool import extract_readme

    extracted_readme_path = extract_readme(tmp_archive)

    assert os.path.isfile(extracted_readme_path)

    with open(extracted_readme_path) as fh:
        readme = yaml.load(fh)

    assert readme['dataset_name'] == 'brassica_rnaseq_reads'
