"""Tests for dtool."""

import os
import json
import shutil
import tempfile
import subprocess
import contextlib
from distutils.dir_util import copy_tree

import yaml
import magic
import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "basic", "output")


#############################################################################
# Test fixtures and helper functions.
#############################################################################

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

    from dtool import new_archive
    from dtool.manifest import create_manifest
    from dtool.archive import create_archive, compress_archive

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


def test_archive_fixture(tmp_archive):

    mimetype = magic.from_file(tmp_archive, mime=True)

    assert mimetype == 'application/x-gzip'


#############################################################################
# Test API helper functions.
#############################################################################

def test_version_is_str():
    from dtool import __version__
    assert isinstance(__version__, str)


#############################################################################
# Test manifest creation functions.
#############################################################################

#############################################################################
# Test new archive functions.
#############################################################################

def test_new_archive(tmp_dir):
    from dtool import new_archive

    dataset_path = new_archive(tmp_dir, no_input=True)

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

    # Test that yaml is valid.
    with open(readme_yml_path, "r") as fh:
        readme_data = yaml.load(fh)
    assert readme_data["dataset_name"] == "brassica_rnaseq_reads"

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


#############################################################################
# Test archive creation functions.
#############################################################################


def test_generate_slurm_submission_script():

    from dtool import generate_slurm_script

    job_parameters = {'n_cores': 8, 'partition': 'rg-sv'}
    command_string = "arctool archive compress -c 8 /tmp/staging/mytar.tar"
    actual_script = generate_slurm_script(command_string,
                                          job_parameters)

    actual = actual_script.split('\n')[-1]

    expected = 'arctool archive compress -c 8 /tmp/staging/mytar.tar'

    assert expected == actual, (expected, actual)


#############################################################################
# Test validation functions.
#############################################################################

def test_summarise_archive(tmp_archive):

    from dtool import summarise_archive

    summary = summarise_archive(tmp_archive)

    assert isinstance(summary, dict)

    assert summary['n_files'] == 3


def test_extract_file(tmp_archive):
    from dtool import extract_file

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
