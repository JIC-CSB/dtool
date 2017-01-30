"""Module containing arctool API."""

import os
import datetime

import yaml

from dtool import (
    log,
    DataSet,
)
from dtool.utils import write_templated_file

HERE = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, '..', 'templates')
README_SCHEMA = [
    ("project_name", u"project_name"),
    ("dataset_name", u"dataset_name"),
    ("confidential", False),
    ("personally_identifiable_information", False),
    ("owner_name", u"Your Name"),
    ("owner_email", u"your.email@example.com"),
    ("owner_username", u"namey"),
    ("date", u"today"),
]


def new_archive_dataset(staging_path, descriptive_metadata):
    """Create new archive in the staging path.

    This creates an initial skeleton directory structure that includes
    a top level README.yml file.

    :param staging_path: path to archiving staging area
    :param descriptive_metadata: dictionary with information which will
                                 populate README.yml
    :returns: (dataset, path to newly created data set archive in
              the staging area)
    """

    dataset_name = descriptive_metadata['dataset_name']
    dataset = DataSet(dataset_name, 'archive')
    dataset_path = os.path.join(staging_path, dataset_name)
    if os.path.isdir(dataset_path):
        raise OSError('Directory already exists: {}'.format(dataset_path))
    os.mkdir(dataset_path)
    dataset.persist_to_path(dataset_path)

    descriptive_metadata.persist_to_path(
        dataset_path, template='arctool_dataset_README.yml')

    # Create a readme file in the archive subdirectory of the dataset
    archive_readme_file_path = os.path.join(dataset_path,
                                            dataset.data_directory,
                                            'README.txt')
    write_templated_file(
        archive_readme_file_path,
        'arctool_archive_dir_README.txt',
        {})

    return dataset, dataset_path, archive_readme_file_path


def readme_yml_is_valid(yml_string):
    """Return True if string representing README.yml content is valid.

    :param yml_string: string representing content of readme file
    :returns: bool
    """
    readme = yaml.load(yml_string)

    if readme is None:
            log("README.yml invalid: empty file")
            return False

    required_keys = ["project_name",
                     "dataset_name",
                     "confidential",
                     "personally_identifiable_information",
                     "owners",
                     "archive_date"]
    for key in required_keys:
        if key not in readme:
            log("README.yml is missing: {}".format(key))
            return False
    if not isinstance(readme["archive_date"], datetime.date):
        log("README.yml invalid: archive_date is not a date")
        return False
    if not isinstance(readme["owners"], list):
        log("README.yml invalid: owners is not a list")
        return False

    for owner in readme["owners"]:
        if "name" not in owner:
            log("README.yml invalid: owner is missing a name")
            return False
        if "email" not in owner:
            log("README.yml invalid: owner is missing an email")
            return False

    return True
