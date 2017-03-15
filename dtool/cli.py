"""Manage datasets."""

import os

import click

from dtoolcore import (
    __version__,
    DataSet,
)
from dtoolcore.filehasher import shasum
from dtool.clickutils import (
    create_project,
    generate_descriptive_metadata,
    info_from_path,
)


#####################################################################
# Helper variables.
#####################################################################

README_SCHEMA = [
    ("project_name", u"project_name"),
    ("dataset_name", u"dataset_name"),
    ("confidential", False),
    ("personally_identifiable_information", False),
    ("owner_name", u"Your Name"),
    ("owner_email", u"your.email@example.com"),
    ("owner_username", u"namey"),
    ("date", u"today"),
]

#####################################################################
# Reusable click decorators.
#####################################################################

dataset_path_option = click.argument(
    'path',
    'Path to dataset directory',
    default=".",
    type=click.Path(exists=True))


#####################################################################
# Command line interface.
#####################################################################


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@dataset_path_option
def info(path):
    message = info_from_path(path)
    print(message)


@cli.command()
@dataset_path_option
def markup(path):
    path = os.path.abspath(path)
    parent_dir = os.path.join(path, "..")
    descriptive_metadata = generate_descriptive_metadata(
        README_SCHEMA, parent_dir)

    dataset_name = descriptive_metadata["dataset_name"]

    descriptive_metadata.persist_to_path(
        path, template='dtool_dataset_README.yml')

    ds = DataSet(dataset_name)
    ds.persist_to_path(path)


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
        dataset_name, template='dtool_dataset_README.yml')

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
@dataset_path_option
def update(path):
    dataset = DataSet.from_path(path)
    dataset.update_manifest()

    click.secho('Updated manifest')
