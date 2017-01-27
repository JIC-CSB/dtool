"""Manage datasets."""

import os
import sys
import getpass

import click

from fluent import sender

from dtool import (
    __version__,
    DataSet,
)
from dtool.clickutils import create_project, generate_descriptive_metadata
from dtool.datatool import README_SCHEMA

logger = sender.FluentSender('arctool', host='v0679', port=24224)


@click.group()
@click.version_option(version=__version__)
@click.option('--fluentd-host', envvar='FLUENTD_HOST', default='v0679')
def cli(fluentd_host):
    logger = sender.FluentSender('arctool', host=fluentd_host, port=24224)
    message = {'api-version': __version__,
               'command_line': sys.argv,
               'unix_username': getpass.getuser()}
    logger.emit('cli_command', message)


@cli.command()
def markup():
    descriptive_metadata = generate_descriptive_metadata(
        README_SCHEMA, '..')

    dataset_name = descriptive_metadata["dataset_name"]

    descriptive_metadata.persist_to_path(
        '.', template='datatool_dataset_README.yml')

    ds = DataSet(dataset_name)
    ds.persist_to_path('.')


@cli.group()
def new():
    pass


@new.command()
def dataset():

    descriptive_metadata = generate_descriptive_metadata(
        README_SCHEMA, '.')

    dataset_name = descriptive_metadata["dataset_name"]
    if os.path.isdir(dataset_name):
        raise OSError('Directory already exists: {}'.format(dataset_name))
    os.mkdir(dataset_name)

    descriptive_metadata.persist_to_path(
        dataset_name, template='datatool_dataset_README.yml')

    ds = DataSet(dataset_name, 'data')
    ds.persist_to_path(dataset_name)


@new.command()
@click.option(
    '--base-path',
    help='Path to directory where new project will be created',
    default='.',
    type=click.Path(exists=True))
def project(base_path):
    create_project(base_path)


@cli.group()
def manifest():
    pass


@manifest.command()
@click.argument('path', 'Path to dataset directory.',
                type=click.Path(exists=True))
def update(path):
    logger.emit('pre_update_manifest', {'path': path})

    dataset = DataSet.from_path(path)
    dataset.update_manifest()

    click.secho('Updated manifest')

    log_data = {'uuid': dataset.uuid,
                'manifest': dataset.manifest}
    logger.emit('post_update_manifest', log_data)
