#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json

import yaml

__version__ = "0.6.1"

VERBOSE = True


class DataSet(object):

    @classmethod
    def from_path(cls, path):
        dataset_info_file = os.path.join(path, '.dtool-dataset')

        with open(dataset_info_file) as fh:
            dataset_info = json.load(fh)

        dataset = cls()

        dataset.name = dataset_info['dataset_name']
        dataset.uuid = dataset_info['uuid']
        dataset.readme_file = os.path.join(path, 'README.yml')

        return dataset

    @property
    def metadata(self):

        with open(self.readme_file) as fh:
            return yaml.load(fh)


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)
