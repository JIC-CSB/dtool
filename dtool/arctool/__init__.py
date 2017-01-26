"""Module containing arctool API."""

import os
import json
import datetime

import yaml

from dtool import (
    log,
    DataSet,
)
from dtool.archive import ArchiveFile
from dtool.manifest import (
    generate_manifest,
)
from dtool.utils import write_templated_file

HERE = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, '..', 'templates')


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

    write_templated_file(
        dataset.abs_readme_path,
        'arctool_dataset_README.yml',
        descriptive_metadata)

    # Create a readme file in the archive subdirectory of the dataset
    archive_readme_file_path = os.path.join(dataset_path,
                                            dataset.data_directory,
                                            'README.txt')
    write_templated_file(
        archive_readme_file_path,
        'arctool_archive_dir_README.txt',
        {})

    return dataset, dataset_path, archive_readme_file_path


def create_manifest(path):
    """Create manifest for all files in directory under the given path.

    The manifest is created one level up from the given path.
    This makes the function idempotent, i.e. if it was run again it
    would create an identical file. This would not be the case if the
    manifest was created in the given path.

    :param path: path to directory with data
    :returns: path to created manifest
    """
    path = os.path.abspath(path)
    archive_root_path, _ = os.path.split(path)
    manifest_filename = os.path.join(archive_root_path, 'manifest.json')

    manifest_data = generate_manifest(path)

    with open(manifest_filename, 'w') as f:
        json.dump(manifest_data, f, indent=4)

    return manifest_filename


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


def rel_paths_for_archiving(path):
    """Return list of relative paths for archiving and total size.

    :param path: path to directory for archiving
    :returns: list of relative paths for archiving, and total size of files
    """
    rel_paths = list(ArchiveFile.header_file_order)
    tot_size = 0

    for rp in rel_paths:
        ap = os.path.join(path, rp)
        tot_size = tot_size + os.stat(ap).st_size

    with open(os.path.join(path, "manifest.json")) as fh:
        manifest = json.load(fh)

    for entry in manifest["file_list"]:
        tot_size = tot_size + entry["size"]
        rpath = os.path.join("archive", entry["path"])
        rel_paths.append(rpath)

    return rel_paths, tot_size
