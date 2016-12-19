"""Module for generating manifests of data directories."""

import os
import json

import magic

from dtool import log, __version__
from dtool.filehasher import generate_file_hash


def file_metadata(path):
    """Return dictionary with file metadata.

    The metadata includes:

    * hash
    * mtime (last modified time)
    * size
    * mimetype

    :param path: path to file
    :returns: dictionary with file metadata
    """
    return dict(hash=generate_file_hash(path),
                size=os.stat(path).st_size,
                mtime=os.stat(path).st_mtime,
                mimetype=magic.from_file(path, mime=True))


def generate_manifest(path):
    """Return archive manifest data structure.

    At the top level the manifest includes:

    * file_list (dictionary with metadata described belwo)
    * hash_function (name of hash function used)

    The file_list includes all files in the file system rooted at path with:

    * relative path
    * hash
    * mtime (last modification time)
    * size
    * mimetype

    :param path: path to directory with data
    :returns: manifest represented as a dictionary
    """

    full_file_list = generate_full_file_list(path)

    log('Building manifest')
    entries = []
    for n, filename in enumerate(full_file_list):
        log('Processing ({}/{}) {}'.format(1+n, len(full_file_list), filename))
        fq_filename = os.path.join(path, filename)
        entry = file_metadata(fq_filename)
        entry['path'] = filename
        entries.append(entry)

    manifest = dict(file_list=entries,
                    dtool_version=__version__,
                    hash_function=generate_file_hash.name)

    return manifest


def generate_full_file_list(path):
    """Return list of paths to all files in tree under path.

    :param path: path to directory with data
    :returns: list of fully qualified paths to all files in directories under
              the path
    """
    path = os.path.abspath(path)
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
    :returns: path to created manifest
    """
    path = os.path.abspath(path)
    archive_root_path, _ = os.path.split(path)
    manifest_filename = os.path.join(archive_root_path, 'manifest.json')

    manifest_data = generate_manifest(path)

    with open(manifest_filename, 'w') as f:
        json.dump(manifest_data, f, indent=4)

    return manifest_filename
