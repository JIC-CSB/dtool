"""Module for generating manifests of data directories."""

import os

import magic

from dtool import log, __version__
from dtool.filehasher import generate_file_hash


def generate_relative_paths(path):
    """Return list of relative paths to all files in tree under path.

    :param path: path to directory with data
    :returns: list of fully qualified paths to all files in directories under
              the path
    """
    path = os.path.abspath(path)
    path_length = len(path) + 1

    relative_path_list = []

    log('Generating relative path list')

    for dirpath, dirnames, filenames in os.walk(path):
        for fn in filenames:
            relative_path = os.path.join(dirpath, fn)
            relative_path_list.append(relative_path[path_length:])

    return relative_path_list


def generate_filedict_list(rel_path_list):

    filedict_list = []
    for rel_path in rel_path_list:
        filedict_list.append(dict(path=rel_path))

    return filedict_list


def apply_filedict_update(path_root, filedict_list, generate_dict_func):

    for item in filedict_list:
        rel_path = item['path']
        abs_path = os.path.join(path_root, rel_path)
        extra_data = generate_dict_func(abs_path)
        item.update(extra_data)


def file_size_dict(abs_file_path):

    size = os.stat(abs_file_path).st_size

    return dict(size=size)


def create_filedict_manifest(path):

    rel_path_list = generate_relative_paths(path)
    filedict_list = generate_filedict_list(rel_path_list)
    apply_filedict_update(path, filedict_list, file_size_dict)

    return filedict_list


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

    full_file_list = generate_relative_paths(path)

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
