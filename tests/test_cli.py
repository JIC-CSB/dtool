"""Tests for the arctool cli."""

import os
import tempfile
import shutil
import subprocess
from distutils.dir_util import copy_tree

import pytest

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")
TEST_OUTPUT_DATA = os.path.join(HERE, "data", "basic", "output")


@pytest.fixture
def chdir(request):
    d = tempfile.mkdtemp()

    cwd = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(cwd)
        shutil.rmtree(d)


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_everything_except_new_archive(tmp_dir):
    from dtool import new_archive

    extra_context = dict(project_name="some_project",
                         dataset_name="data_set_1")
    dataset_path = new_archive(tmp_dir,
                               extra_context=extra_context,
                               no_input=True)
    assert os.path.isdir(dataset_path)

    archive_input_path = os.path.join(TEST_INPUT_DATA, 'archive')
    archive_output_path = os.path.join(dataset_path, 'archive')
    copy_tree(archive_input_path, archive_output_path)

    cmd = ["arctool", "--version"]
    subprocess.call(cmd)

    cmd = ["arctool", "manifest", "create", archive_output_path]
    subprocess.call(cmd)
    manifest_path = os.path.join(dataset_path, "manifest.json")
    assert os.path.isfile(manifest_path)

    cmd = ["arctool", "archive", "create", dataset_path]
    subprocess.call(cmd)
    tar_path = os.path.join(tmp_dir, "data_set_1.tar")
    assert os.path.isfile(tar_path)

    cmd = ["arctool", "archive", "compress", tar_path]
    subprocess.call(cmd)
    gzip_path = os.path.join(tmp_dir, "data_set_1.tar.gz")
    assert os.path.isfile(gzip_path)

    # Remove the dataset path to ensure that files are actually extracted.
    shutil.rmtree(dataset_path)

    cmd = ["arctool", "extract", "readme", gzip_path]
    subprocess.call(cmd)
    readme_path = os.path.join(dataset_path, "README.yml")
    assert os.path.isfile(readme_path)

    cmd = ["arctool", "extract", "manifest", gzip_path]
    subprocess.call(cmd)
    manifest_path = os.path.join(dataset_path, "manifest.json")
    assert os.path.isfile(manifest_path)

    cmd = ["arctool", "verify", "summary", gzip_path]
    subprocess.call(cmd)
