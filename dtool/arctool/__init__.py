"""Module containing arctool API."""

import os
import json
import uuid
import tarfile
import getpass
import datetime

import yaml
from jinja2 import Environment, PackageLoader

from cookiecutter.main import cookiecutter

from dtool import (
    __version__,
    log,
)
from dtool.manifest import (
    generate_manifest,
)
from dtool.archive import (
    initialise_tar_archive,
    append_to_tar_archive,
    extract_file,
    icreate_collection,
    is_collection,
)

HERE = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, '..', 'templates')


class Project(object):
    """Arctool project as a collection of datasets."""

    def __init__(self, staging_path, project_name):
        self.path = icreate_collection(staging_path, project_name)
        self.readme_file = os.path.join(self.path, 'README.yml')
        self.name = project_name

        self._safe_create_readme()

    @classmethod
    def from_path(cls, project_path):

        if not is_collection(project_path):
            raise ValueError('Not a project: {}'.format(project_path))

        readme_file = os.path.join(project_path, 'README.yml')

        with open(readme_file) as fh:
            project_name = yaml.load(fh)['project_name']

        staging_path = os.path.join(project_path, '..')
        return cls(staging_path, project_name)

    def _safe_create_readme(self):

        if os.path.isfile(self.readme_file):
            return

        env = Environment(loader=PackageLoader('dtool', 'templates'),
                          keep_trailing_newline=True)

        readme_template = env.get_template('arctool_project_README.yml')

        project_metadata = {'project_name': self.name}

        with open(self.readme_file, 'w') as fh:
            fh.write(readme_template.render(project_metadata))

    @property
    def metadata(self):

        with open(self.readme_file) as fh:
            return yaml.load(fh)


def new_archive_dataset(staging_path, extra_context=dict(), no_input=False):
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

    readme_path = os.path.join(archive_path, 'README.yml')
    with open(readme_path) as fh:
        readme = yaml.load(fh)
    dataset_name = readme['dataset_name']

    dataset_file_path = os.path.join(archive_path, '.dtool-dataset')

    dataset_uuid = str(uuid.uuid4())
    dataset_info = {'dtool_version': __version__,
                    'dataset_name': dataset_name,
                    'uuid': dataset_uuid,
                    'unix_username': unix_username,
                    'manifest_root': 'archive'}

    with open(dataset_file_path, 'w') as f:
        json.dump(dataset_info, f)

    return archive_path


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
    rel_paths = [u".dtool-dataset",
                 u"README.yml",
                 u"manifest.json"]
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


def initialise_archive(path):

    initial_files = [u".dtool-dataset",
                     u"README.yml",
                     u"manifest.json"]

    first_file = initial_files[0]

    tar_output_path = initialise_tar_archive(path, first_file)

    for file in initial_files[1:]:
        append_to_tar_archive(path, file)

    return tar_output_path


# Should this function be deprecated?
# It is no longer used by the arctool cli.
def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

    tar_output_path = initialise_archive(path)

    manifest_path = os.path.join(path, 'manifest.json')
    with open(manifest_path) as fh:
        manifest = json.load(fh)

    filedict_manifest = manifest["file_list"]

    for entry in filedict_manifest:
        rel_path = entry['path']
        rel_path = os.path.join('archive', entry['path'])
        append_to_tar_archive(path, rel_path)

    return tar_output_path


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
