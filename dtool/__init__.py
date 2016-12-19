#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json
import uuid
import tarfile
import subprocess
import getpass
import datetime

import yaml
from jinja2 import Environment, PackageLoader

from cookiecutter.main import cookiecutter

VERBOSE = True

HERE = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, 'templates')

__version__ = "0.5.0"


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)


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


def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    :returns: path to created tarball
    """

    path = os.path.abspath(path)
    staging_path, dataset_name = os.path.split(path)

    tar_output_filename = dataset_name + '.tar'

    dataset_info_path = os.path.join(dataset_name, '.dtool-dataset')
    tar_dataset_info = ['tar', '-cf', tar_output_filename, dataset_info_path]
    subprocess.call(tar_dataset_info, cwd=staging_path)

    readme_path = os.path.join(dataset_name, 'README.yml')
    tar_readme = ['tar', '-rf', tar_output_filename, readme_path]
    subprocess.call(tar_readme, cwd=staging_path)

    manifest_path = os.path.join(dataset_name, 'manifest.json')
    tar_manifest = ['tar', '-rf', tar_output_filename, manifest_path]
    subprocess.call(tar_manifest, cwd=staging_path)

    exclude_manifest = '--exclude={}'.format(manifest_path)
    exclude_readme = '--exclude={}'.format(readme_path)
    exclude_dataset_info = '--exclude={}'.format(dataset_info_path)
    tar_remainder = ['tar',
                     exclude_manifest,
                     exclude_readme,
                     exclude_dataset_info,
                     '-rf',
                     tar_output_filename,
                     dataset_name]

    subprocess.call(tar_remainder, cwd=staging_path)

    tar_output_path = os.path.join(staging_path, tar_output_filename)
    tar_output_path = os.path.abspath(tar_output_path)

    return tar_output_path


def compress_archive(path, n_threads=8):
    """Compress the (tar) archive at the given path.

    Uses pigz for speed.

    :param path: path to the archive tarball
    :param n_threads: number of threads for pigz to use
    :returns: path to created gzip file
    """
    path = os.path.abspath(path)

    basename = os.path.basename(path)
    archive_name, ext = os.path.splitext(basename)
    assert ext == '.tar'

    compress_tool = 'pigz'
    compress_args = ['-p', str(n_threads), path]
    compress_command = [compress_tool] + compress_args

    subprocess.call(compress_command)

    return path + '.gz'


def generate_slurm_script(command_string, job_parameters):
    """Return slurm script.

    :param command_string: command to run in slurm script
    :param job_parameters: dictionary of job parameters
    :returns: slurm sbatch script
    """
    slurm_templates = os.path.join('templates', 'slurm_submission')
    env = Environment(loader=PackageLoader('dtool', slurm_templates))

    template = env.get_template('submit_command.slurm.j2')

    return template.render(job=job_parameters, command_string=command_string)


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


def extract_file(archive_path, file_in_archive):
    """Extract a file from an archive.

    The archive can be a tarball or a compressed tarball.

    :param archive_path: path to the archive to extract a file from
    :param file_in_archive: file to extract
    :returns: path to extracted file
    """
    archive_path = os.path.abspath(archive_path)

    archive_basename = os.path.basename(archive_path)
    archive_dirname = os.path.dirname(archive_path)
    archive_name, exts = archive_basename.split('.', 1)
    assert "tar" in exts.split(".")  # exts is expected to be tar or tar.gz

    extract_path = os.path.join(archive_name, file_in_archive)
    with tarfile.open(archive_path, 'r:*') as tar:
        tar.extract(extract_path, path=archive_dirname)

    return os.path.join(archive_dirname, extract_path)


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
