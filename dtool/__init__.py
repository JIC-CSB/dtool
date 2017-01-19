#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json
import uuid
import getpass

import yaml
from jinja2 import Environment, PackageLoader

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

        with open(self.abs_readme_path, 'w') as fh:
            fh.write("")

        with open(self._abs_manifest_path, 'w') as fh:
            fh.write("")

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
