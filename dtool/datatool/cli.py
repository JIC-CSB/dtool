"""Manage datasets."""

import os
import sys
import json
import getpass

import click

from fluent import sender

from dtool import __version__, DataSet, DescriptiveMetadata
from dtool.arctool import create_manifest
from dtool.utils import write_templated_file, auto_metadata

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


@cli.group()
def new():
    pass


@new.command()
def dataset():
    readme_info = [
        ("project_name", "project_name"),
        ("dataset_name", "dataset_name"),
        ("confidential", False),
        ("personally_identifiable_information", False),
        ("owner_name", "Your Name"),
        ("owner_email", "your.email@example.com"),
        ("owner_username", "namey"),
        ("date", "today"),
    ]
    descriptive_metadata = DescriptiveMetadata(readme_info)
    descriptive_metadata.update(auto_metadata("nbi.ac.uk"))
    descriptive_metadata.prompt_for_values()
    dataset_name = descriptive_metadata["dataset_name"]

    if os.path.isdir(dataset_name):
        raise OSError('Directory already exists: {}'.format(dataset_name))

    os.mkdir(dataset_name)

    ds = DataSet(dataset_name, 'data')
    ds.persist_to_path(descriptive_metadata["dataset_name"])

    write_templated_file(ds.abs_readme_path,
                         'datatool_dataset_README.yml',
                         descriptive_metadata)


@cli.group()
def manifest():
    pass


@manifest.command()
@click.argument('path', 'Path to archive directory.',
                type=click.Path(exists=True))
def create(path):
    logger.emit('pre_create_manifest', {'path': path})

    manifest_path = create_manifest(path)

    with open(manifest_path) as fh:
        manifest = json.load(fh)

    click.secho('Created manifest: ', nl=False)
    click.secho(manifest_path, fg='green')

    log_data = {'manifest_path': manifest_path,
                'manifest': manifest}
    logger.emit('post_create_manifest', log_data)
