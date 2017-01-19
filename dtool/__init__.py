#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json
import uuid
import getpass

import yaml
import magic
from jinja2 import Environment, PackageLoader

from dtool.filehasher import generate_file_hash

__version__ = "0.7.0"

VERBOSE = True

# admin/administrative metadata - .dtool/dtool
# descriptive metadata - README.yml
# structural metadata - manifest.json


class DataSet(object):
    """Class for representing datasets."""

    def __init__(self, name, data_directory='.'):
        self._admin_metadata = {'uuid': str(uuid.uuid4()),
                                'name': name,
                                'type': 'dataset',
                                'dtool_version': __version__,
                                'readme_path': 'README.yml',
                                'manifest_path': os.path.join(
                                    '.dtool', 'manifest.json'),
                                'unix_username': getpass.getuser(),
                                'manifest_root': data_directory}
        self._abs_path = None

    def __eq__(self, other):
        return self._admin_metadata == other._admin_metadata

    @property
    def uuid(self):
        return self._admin_metadata['uuid']

    @property
    def name(self):
        return self._admin_metadata['name']

    @property
    def dtool_version(self):
        return self._admin_metadata['dtool_version']

    @property
    def unix_username(self):
        return self._admin_metadata['unix_username']

    @property
    def abs_readme_path(self):
        if self._abs_path is None:
            return None
        return os.path.join(self._abs_path,
            self._admin_metadata['readme_path'])

    @property
    def _abs_manifest_path(self):
        if self._abs_path is None:
            return None
        return os.path.join(self._abs_path,
            self._admin_metadata['manifest_path'])

    def persist_to_path(self, path):
        """Mark up a directory as a DataSet"""

        path = os.path.abspath(path)
        self._abs_path = path
        data_directory = os.path.join(path,
            self._admin_metadata['manifest_root'])

        if not os.path.isdir(data_directory):
            os.mkdir(data_directory)

        dtool_dir_path = os.path.join(path, '.dtool')
        os.mkdir(dtool_dir_path)

        if not os.path.isfile(self.abs_readme_path):
            with open(self.abs_readme_path, 'w') as fh:
                fh.write("")

        abs_manifest_root = os.path.join(path,
            self._admin_metadata['manifest_root'])
        manifest = generate_manifest(abs_manifest_root)
        with open(self._abs_manifest_path, 'w') as fh:
            json.dump(manifest, fh)

        dtool_file_path = os.path.join(dtool_dir_path, 'dtool')
        with open(dtool_file_path, 'w') as fh:
            json.dump(self._admin_metadata, fh)


class oldDataSet(object):

    def __init__(self, name, manifest_root='data'):

        self.uuid = str(uuid.uuid4())
        self.manifest_root = manifest_root
        # .dtool/dtool
        self.admin_metadata = {'dataset_name': name,
                               'type': 'dataset'}
        # README.yml
        self.descriptive_metadata = {'dataset_name': name}

    @classmethod
    def from_path(cls, path):
        dataset_info_file = os.path.join(path, '.dtool-dataset')

        with open(dataset_info_file) as fh:
            dataset_info = json.load(fh)

        dataset = cls(dataset_info['dataset_name'])
        dataset.admin_metadata = dataset_info

        dataset.uuid = dataset_info['uuid']
        dataset.readme_path = os.path.join(path, 'README.yml')
        dataset._replace_descriptive_metadata()

        return dataset

    @property
    def name(self):
        return self.admin_metadata['dataset_name']

    def _replace_descriptive_metadata(self):

        with open(self.readme_path) as fh:
            self.descriptive_metadata = yaml.load(fh)

    def persist_to_path(self, path, readme_template=None):

        path = os.path.abspath(path)

        self.dataset_path = os.path.join(path, self.name)
        os.mkdir(self.dataset_path)

        data_path = os.path.join(self.dataset_path, self.manifest_root)
        os.mkdir(data_path)

        if readme_template is None:
            env = Environment(loader=PackageLoader('dtool', 'templates'),
                              keep_trailing_newline=True)

            readme_template = env.get_template('dtool_dataset_README.yml')

        self.readme_path = os.path.join(self.dataset_path, 'README.yml')
        with open(self.readme_path, 'w') as fh:
            fh.write(readme_template.render(self.descriptive_metadata))

        unix_username = getpass.getuser()
        self._info_path = os.path.join(self.dataset_path, '.dtool-dataset')
        dataset_info = {'dtool_version': __version__,
                        'type': 'dataset',
                        'dataset_name': self.name,
                        'uuid': self.uuid,
                        'unix_username': unix_username,
                        'readme_path': os.path.relpath(self.readme_path,
                                                       self.dataset_path),
                        'manifest_root': self.manifest_root}
        with open(self._info_path, 'w') as fh:
            json.dump(dataset_info, fh)

        return self.dataset_path


class Collection(object):
    """Class for representing collections of data sets."""

    def __init__(self):
        self._admin_metadata = {"type": "collection",
                                "uuid": str(uuid.uuid4()),
                                "readme_path": "README.yml",
                                "dtool_version": __version__}
        self._abs_path = None

    def __eq__(self, other):
        return self._admin_metadata == other._admin_metadata

    @property
    def uuid(self):
        return self._admin_metadata['uuid']

    @property
    def dtool_version(self):
        return self._admin_metadata['dtool_version']

    @property
    def abs_readme_path(self):
        if self._abs_path is None:
            return None
        return os.path.join(self._abs_path,
            self._admin_metadata['readme_path'])

    @property
    def descriptive_metadata(self):
        """Return descriptive metadata as a dictionary.

        Read in from README.yml dynamically. Returns empty dictionary
        if file does not exist or is empty.

        Current implementation will return list if README.yml contains
        list as top level data structure.
        """
        if self.abs_readme_path is not None:
            with open(self.abs_readme_path) as fh:
                contents = yaml.load(fh)
                if contents:
                    return contents
        return {}

    @classmethod
    def from_path(cls, path):
        """Return instance of Collection instantiated from path."""

        collection = Collection()

        dtool_file_path = os.path.join(path, '.dtool', 'dtool')
        if not os.path.isfile(dtool_file_path):
            raise ValueError('Not a collection; .dtool/dtool does not exist')

        with open(dtool_file_path) as fh:
            collection._admin_metadata = json.load(fh)

        if 'type' not in collection._admin_metadata:
            raise ValueError(
                'Not a collection; no type definition in .dtool/dtool')

        if collection._admin_metadata['type'] != 'collection':
            raise ValueError(
                'Not a collection; wrong type definition in .dtool/dtool')

        return collection

    def persist_to_path(self, path):
        """Mark up a directory as a collection."""
        path = os.path.abspath(path)
        self._abs_path = path
        dtool_dir_path = os.path.join(path, ".dtool")
        dtool_file_path = os.path.join(dtool_dir_path, "dtool")
        os.mkdir(dtool_dir_path)
        if not os.path.isfile(self.abs_readme_path):
            with open(self.abs_readme_path, "w") as fh:
                fh.write("")
        with open(dtool_file_path, "w") as fh:
            json.dump(self._admin_metadata, fh)


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)

###################################################
# STOLEN FROM MANIFEST. PUT IT BACK LATER. MAYBE. #
###################################################

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
