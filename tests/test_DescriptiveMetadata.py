"""Test the DescriptiveMetadata class."""

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


def test_DescriptiveMetadata_initialisation():
    from dtool.metadata import DescriptiveMetadata
    descriptive_metadata = DescriptiveMetadata()
    assert descriptive_metadata.ordered_keys == []

    schema = [("project_name", "my_project")]
    descriptive_metadata = DescriptiveMetadata(schema=schema)
    assert descriptive_metadata.ordered_keys == ["project_name"]
    assert descriptive_metadata._dict == {"project_name": "my_project"}

    schema = [("project_name", "my_project"),
              ("aaa", "bbb")]
    descriptive_metadata = DescriptiveMetadata(schema=schema)
    assert descriptive_metadata.ordered_keys == ["project_name", "aaa"]


def test_DescriptiveMetadata_update():
    from dtool.metadata import DescriptiveMetadata
    schema = [("project_name", "my_project"),
              ("aaa", "bbb")]
    descriptive_metadata = DescriptiveMetadata(schema=schema)
    descriptive_metadata.update({"project_name": "rnaseq"})
    assert descriptive_metadata["project_name"] == "rnaseq"

    descriptive_metadata.update({"new_prop": "test"})
    assert descriptive_metadata["new_prop"] == "test"

    assert set(descriptive_metadata._dict.keys()) \
        == set(descriptive_metadata.keys())


def test_DescriptiveMetadata_works_with_templating():
    from dtool.metadata import DescriptiveMetadata
    schema = [("project_name", "my_project")]
    descriptive_metadata = DescriptiveMetadata(schema)

    from jinja2 import Template
    template = Template("project_name: {{ project_name }}")

    output = template.render(descriptive_metadata)

    assert output == 'project_name: my_project'


def test_DescriptiveMetadata_iter_keys_and_defaults():
    from dtool.metadata import DescriptiveMetadata
    schema = [("project_name", "old_project"),
              ("dataset_name", "old_dataset")]
    descriptive_metadata = DescriptiveMetadata(schema)
    extra_data = dict([("dataset_name", "new_dataset"),
                       ("extra_property", "something")])
    descriptive_metadata.update(extra_data)

    keys_and_defaults = [i for i in descriptive_metadata]
    assert keys_and_defaults == [("project_name", "old_project"),
                                 ("dataset_name", "new_dataset"),
                                 ("extra_property", "something")]


def test_DescriptiveMetadata_prompt_for_values():
    from dtool.metadata import DescriptiveMetadata
    schema = [("project_name", "old_project"),
              ("dataset_name", "old_dataset")]
    descriptive_metadata = DescriptiveMetadata(schema)

    import click
    from click.testing import CliRunner

    runner = CliRunner()

    @click.command()
    def prompt_assist():
        descriptive_metadata.prompt_for_values()

    input_string = 'new_project\n\n'
    result = runner.invoke(prompt_assist, input=input_string)

    assert not result.exception

    assert descriptive_metadata['project_name'] == 'new_project'


def test_DescriptiveMetadata_persist_to_file(tmp_dir):
    from dtool.metadata import DescriptiveMetadata
    from dtool.cli import README_SCHEMA
    descriptive_metadata = DescriptiveMetadata(README_SCHEMA)

    output_file = os.path.join(tmp_dir, 'README.yml')
    descriptive_metadata.persist_to_path(tmp_dir)

    assert os.path.isfile(output_file)

    with open(output_file) as fh:
        contents = fh.read()

    assert contents == """---

project_name: project_name
dataset_name: dataset_name
confidential: False
personally_identifiable_information: False
owner_name: Your Name
owner_email: your.email@example.com
owner_username: namey
date: today
"""

    descriptive_metadata.persist_to_path(
        tmp_dir, template='dtool_dataset_README.yml')

    with open(output_file) as fh:
        contents = fh.read()

    assert contents == """---

project_name: project_name
dataset_name: dataset_name
confidential: False
personally_identifiable_information: False
owners:
  - name: Your Name
    email: your.email@example.com
    username: namey
creation_date: today
# links:
#  - http://doi.dx.org/your_doi
#  - http://github.com/your_code_repository
# budget_codes:
#  - E.g. CCBS1H10S
"""
