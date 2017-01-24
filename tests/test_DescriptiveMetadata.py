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
