"""Manage datasets."""

import os

import click

from dtool import (
    __version__,
    DataSet,
)
from dtool.clickutils import (
    create_project,
    generate_descriptive_metadata,
    info_from_path,
)

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


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
def info():
    message = info_from_path(".")
    print(message)


@cli.command()
def markup():
    descriptive_metadata = generate_descriptive_metadata(
        README_SCHEMA, '..')

    dataset_name = descriptive_metadata["dataset_name"]

    descriptive_metadata.persist_to_path(
        '.', template='dtool_dataset_README.yml')

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
@click.argument('path', 'Path to dataset directory.',
                type=click.Path(exists=True))
def update(path):
    dataset = DataSet.from_path(path)
    dataset.update_manifest()

    click.secho('Updated manifest')
