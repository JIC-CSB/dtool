"""Module containing arctool API."""

import os
import json
import tarfile
import datetime

import yaml

from jinja2 import Environment, PackageLoader

from dtool import (
    log,
    DataSet,
)
from dtool.archive import ArchiveDataSet, ArchiveFile
from dtool.manifest import (
    generate_manifest,
)
from dtool.archive import (
#   initialise_tar_archive,
#   append_to_tar_archive,
    extract_file,
    icreate_collection,
    is_collection,
)
from dtool.utils import write_templated_file

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


def initialise_archive(path):
    pass

#   initial_files = [u".dtool-dataset",
#                    u"README.yml",
#                    u"manifest.json"]

#   first_file = initial_files[0]

#   tar_output_path = initialise_tar_archive(path, first_file)

#   for file in initial_files[1:]:
#       append_to_tar_archive(path, file)

#   return tar_output_path



# Should this function be deprecated?
# It is no longer used by the arctool cli.
def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

#   tar_output_path = initialise_archive(path)

#   manifest_path = os.path.join(path, 'manifest.json')
#   with open(manifest_path) as fh:
#       manifest = json.load(fh)

#   filedict_manifest = manifest["file_list"]

#   for entry in filedict_manifest:
#       rel_path = entry['path']
#       rel_path = os.path.join('archive', entry['path'])
#       append_to_tar_archive(path, rel_path)

#   return tar_output_path
    archive_dataset = ArchiveDataSet.from_path(path)
    archive_file = ArchiveFile(archive_dataset)
    output_path = os.path.join(path, "..")
    return archive_file.persist_to_tar(output_path)


def summarise_archive(path):
    """Return dictionary with summary information about an archive.

    :param path: path to archive tar gzipped file
    :returns: dictionary of summary information about the archive
    """
    path = os.path.abspath(path)

    archive_basename = os.path.basename(path)
    archive_name, exts = archive_basename.split('.', 1)
    assert exts == 'tar.gz'

    manifest_path = os.path.join(archive_name, '.dtool/manifest.json')

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
    return extract_file(archive_path, ".dtool/manifest.json")


def extract_readme(archive_path):
    """Extract readme from archive into directory where archive is located.

    :param archive_path: path to archive
    :returns: path to extracted readme file
    """
    return extract_file(archive_path, "README.yml")
