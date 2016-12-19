"""Module containing arctool API."""

import os
import json
import uuid
import tarfile
import getpass
import datetime

import yaml

from cookiecutter.main import cookiecutter

from dtool import __version__, log
from dtool.manifest import generate_manifest
from dtool.archive import extract_file

HERE = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, 'templates')


def new_archive(staging_path, extra_context=dict(), no_input=False):
    """Create new archive in the staging path.

    This creates an initial skeleton directory structure that includes
    a top level README.yml file.

    The extra_context parameter can be used to provide values for the
    cookiecutter template. See the
    dtool/templates/archive/cookicutter.json file for keys and
    default values.

    The no_input parameter exists for automated testing purposes.
    If it is set to True it disables prompting of user input.

    :param staging_path: path to archiving staging area
    :param extra_context: dictionary with context for cookiecutter template
    :returns: path to newly created data set archive in the staging area
    """
    unix_username = getpass.getuser()
    email = "{}@nbi.ac.uk".format(unix_username)
    archive_template = os.path.join(TEMPLATE_DIR, 'archive')
    if "owner_unix_username" not in extra_context:
        extra_context["owner_unix_username"] = unix_username
    if "owner_email" not in extra_context:
        extra_context["owner_email"] = email
    extra_context["version"] = __version__
    archive_path = cookiecutter(archive_template,
                                output_dir=staging_path,
                                no_input=no_input,
                                extra_context=extra_context)

    dataset_file_path = os.path.join(archive_path, '.dtool-dataset')

    dataset_uuid = str(uuid.uuid4())
    dataset_info = {'dtool_version': __version__,
                    'uuid': dataset_uuid,
                    'unix_username': unix_username}

    with open(dataset_file_path, 'w') as f:
        json.dump(dataset_info, f)

    return archive_path


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


def summarise_archive(path):
    """Return dictionary with summary information about an archive.

    :param path: path to archive tar gzipped file
    :returns: dictionary of summary information about the archive
    """
    path = os.path.abspath(path)

    archive_basename = os.path.basename(path)
    archive_name, exts = archive_basename.split('.', 1)
    assert exts == 'tar.gz'

    manifest_path = os.path.join(archive_name, 'manifest.json')

    with tarfile.open(path, 'r:gz') as tar:
        manifest_fp = tar.extractfile(manifest_path)
        manifest_str = manifest_fp.read().decode("utf-8")
        manifest = json.loads(manifest_str)

    total_size = sum(entry['size'] for entry in manifest['file_list'])

    summary = {}
    summary['n_files'] = len(manifest['file_list'])
    summary['total_size'] = total_size
    summary['manifest'] = manifest

    return summary


def extract_manifest(archive_path):
    """Extract manifest from archive into directory where archive is located.

    :param archive_path: path to archive
    :returns: path to extracted manifest file
    """
    return extract_file(archive_path, "manifest.json")


def extract_readme(archive_path):
    """Extract readme from archive into directory where archive is located.

    :param archive_path: path to archive
    :returns: path to extracted readme file
    """
    return extract_file(archive_path, "README.yml")
