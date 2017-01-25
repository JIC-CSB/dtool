"""Test the DescriptiveMetadata class."""


def test_DescriptiveMetadata_initialisation():
    from dtool import DescriptiveMetadata
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
    from dtool import DescriptiveMetadata
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
    from dtool import DescriptiveMetadata
    schema = [("project_name", "my_project")]
    descriptive_metadata = DescriptiveMetadata(schema)

    from jinja2 import PackageLoader, Environment

    env = Environment(loader=PackageLoader('dtool', 'templates'),
                      keep_trailing_newline=True)
    template = env.get_template('arctool_project_README.yml')

    output = template.render(descriptive_metadata)

    assert output == '---\n\nproject_name: my_project\n'


def test_DescriptiveMetadata_iter_keys_and_defaults():
    from dtool import DescriptiveMetadata
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


# def test_DescriptiveMetadata_prompt_for_values():
#     from dtool import DescriptiveMetadata
#     schema = [("project_name", "old_project"),
#               ("dataset_name", "old_dataset")]
#     descriptive_metadata = DescriptiveMetadata(schema)
#     descriptive_metadata.prompt_for_values()
