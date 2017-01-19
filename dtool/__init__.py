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
        self.uuid = str(uuid.uuid4())
        self.admin_metadata = {"type": "collection", "uuid": self.uuid}

    def persist_to_path(self, path):
        """Mark up a directory as a collection."""
        path = os.path.abspath(path)
        dtool_dir_path = os.path.join(path, ".dtool")
        dtool_file_path = os.path.join(dtool_dir_path, "dtool")
        os.mkdir(dtool_dir_path)
        with open(dtool_file_path, "w") as fh:
            json.dump(self.admin_metadata, fh)


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)
