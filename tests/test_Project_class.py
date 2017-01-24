"""Test the dtool.Project class."""

import os
import shutil
import tempfile

import yaml
import pytest


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


def test_project_initialisation(tmp_dir):
    from dtool import Project

    project = Project('my_project')
    project.persist_to_path(tmp_dir)
    expected_path = os.path.join(tmp_dir, 'README.yml')
    assert os.path.isfile(expected_path)
    with open(expected_path) as fh:
        descriptive_metadata = yaml.load(fh)
    assert descriptive_metadata == project.descriptive_metadata
    assert project.abs_readme_path == expected_path
    assert project.descriptive_metadata == {'project_name': 'my_project'}


def test_create_project_does_not_overwrite_readme(tmp_dir):

    from dtool import Project

    test_project = Project('my_test_project')

    readme_path = os.path.join(tmp_dir, "README.yml")

    with open(readme_path, 'w') as fh:
        fh.write('test')

    test_project.persist_to_path(tmp_dir)

    with open(readme_path) as fh:
        readme_contents = fh.read()

    assert readme_contents == 'test'
