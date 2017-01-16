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


class DataSet(object):

    def __init__(self, name, manifest_root='data'):

        self.uuid = str(uuid.uuid4())
        self.manifest_root = manifest_root
        self.descriptive_metadata = {'dataset_name': name}

    @classmethod
    def from_path(cls, path):
        dataset_info_file = os.path.join(path, '.dtool-dataset')

        with open(dataset_info_file) as fh:
            dataset_info = json.load(fh)

        dataset = cls(dataset_info['dataset_name'])

        dataset.uuid = dataset_info['uuid']
        dataset.readme_file = os.path.join(path, 'README.yml')

        return dataset

    @property
    def name(self):

        return self.descriptive_metadata['dataset_name']

    @property
    def metadata(self):

        with open(self.readme_file) as fh:
            return yaml.load(fh)

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

        unix_username = getpass.getuser()
        self._info_path = os.path.join(self.dataset_path, '.dtool-dataset')
        dataset_info = {'dtool_version': __version__,
                        'dataset_name': self.name,
                        'uuid': self.uuid,
                        'unix_username': unix_username,
                        'manifest_root': self.manifest_root}
        with open(self._info_path, 'w') as fh:
            json.dump(dataset_info, fh)

        self.readme_path = os.path.join(self.dataset_path, 'README.yml')
        with open(self.readme_path, 'w') as fh:
            fh.write(readme_template.render(self.descriptive_metadata))

        return self.dataset_path


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)
