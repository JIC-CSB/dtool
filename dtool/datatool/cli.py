"""Manage datasets."""

import click

from dtool import __version__
from dtool.arctool import create_manifest


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.group()
def manifest():
    pass


@manifest.command()
@click.argument('path', 'Path to archive directory.',
                type=click.Path(exists=True))
def create(path):
    manifest_path = create_manifest(path)
    click.secho('Created manifest: ', nl=False)
    click.secho(manifest_path, fg='green')
