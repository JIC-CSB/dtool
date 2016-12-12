#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json
import hashlib
import tarfile
import subprocess
import getpass

from jinja2 import Environment, PackageLoader

from cookiecutter.main import cookiecutter

VERBOSE = True

HERE = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(HERE, 'templates')


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)


def split_safe_path(path):
    """Return paths where trailing slashes have been stripped.

    Required as os.path.split does not behave ideally.

    :param path: path to be sanitised
    :returns: sanitised path
    """
    return os.path.normpath(path)


def shasum(filename):
    """Return hex digest of SHA-1 hash of file.

    :param filename: path to file
    :returns: shasum of file
    """

    # Tried using Mac native shasum. But this was slower.
    # Maybe not surprising as shasum on Mac was a Perl script,
    # i.e. not a compiled binary.

    BUF_SIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read(BUF_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BUF_SIZE)

    return hasher.hexdigest()


def generate_manifest(path):
    """Return archive manifest data structure.

    Structure includes all files in the file system rooted at path with:

    * Relative path
    * SHA1 hash
    * Last modification time
    * Size

    :param path: path to directory with data
    :returns: manifest represented as a dictionary
    """

    full_file_list = generate_full_file_list(path)

    log('Building manifest')
    entries = []
    for n, filename in enumerate(full_file_list):
        log('Processing ({}/{}) {}'.format(1+n, len(full_file_list), filename))
        fq_filename = os.path.join(path, filename)
        st_size = os.stat(fq_filename).st_size
        st_mtime = os.stat(fq_filename).st_mtime
        file_hash = shasum(fq_filename)

        entry = {}
        entry['path'] = filename
        entry['hash'] = file_hash
        entry['size'] = st_size
        entry['mtime'] = st_mtime
        entries.append(entry)

    manifest = dict(file_list=entries)

    return manifest


def generate_full_file_list(path):
    """Return list of paths to all files in tree under path.

    :param path: path to directory with data
    :returns: list of fully qualified paths to all files in directories under
              the path
    """
    path = split_safe_path(path)
    path_length = len(path) + 1

    file_list = []

    log('Generating file list')

    for dirpath, dirnames, filenames in os.walk(path):
        for fn in filenames:
            relative_path = os.path.join(dirpath, fn)
            file_list.append(relative_path[path_length:])

    return file_list


def create_manifest(path):
    """Create manifest for all files in directory under the given path.

    The manifest is created one level up from the given path.
    This makes the function idempotent, i.e. if it was run again it
    would create an identical file. This would not be the case if the
    manifest was created in the given path.

    :param path: path to directory with data
    """
    path = split_safe_path(path)
    archive_root_path, _ = os.path.split(path)
    manifest_filename = os.path.join(archive_root_path, 'manifest.json')

    manifest_data = generate_manifest(path)

    with open(manifest_filename, 'w') as f:
        json.dump(manifest_data, f, indent=4)

    # Should this return the path to the generated manifest file?


def new_archive(staging_path, no_input=False):
    """Create new archive in the staging path.

    This creates an initial skeleton directory structure that includes
    a top level README.yml file.

    The no_input parameter exists for automated testing purposes.
    If it is set to True it disables prompting of user input.

    :param staging_path: path to archiving staging area
    """
    unix_username = getpass.getuser()
    email = "{}@nbi.ac.uk".format(unix_username)
    archive_template = os.path.join(TEMPLATE_DIR, 'archive')
    extra_context = dict(owner_unix_username=unix_username,
                         owner_email=email)
    cookiecutter(archive_template,
                 output_dir=staging_path,
                 no_input=no_input,
                 extra_context=extra_context)

    # Should this return the path to the newly created archive in the
    # staging area?


def create_archive(path):
    """Create archive from path using tar.

    :param path: path to archive in staging area
    """

    path = os.path.abspath(path)
    path = split_safe_path(path)
    staging_path, dataset_name = os.path.split(path)

    tar_output_filename = dataset_name + '.tar'

    tar_command = ['tar', '-cf', tar_output_filename, dataset_name]

    subprocess.call(tar_command, cwd=staging_path)

    # Should this return the path to the newly created tarball?


def compress_archive(path, n_threads=8):
    """Compress the (tar) archive at the given path.

    Uses pigz for speed.

    :param path: path to the archive tarball
    :param n_threads: number of threads for pigz to use
    """
    path = os.path.abspath(path)

    compress_tool = 'pigz'
    compress_args = ['-p', str(n_threads), path]
    compress_command = [compress_tool] + compress_args

    subprocess.call(compress_command)

    # Should this return the path to the gzip file.


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
        manifest = json.load(manifest_fp)

    total_size = sum(entry['size'] for entry in manifest['file_list'])

    summary = {}
    summary['n_files'] = len(manifest['file_list'])
    summary['total_size'] = total_size
    summary['manifest'] = manifest

    return summary
