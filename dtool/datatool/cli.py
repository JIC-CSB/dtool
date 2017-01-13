"""Manage datasets."""

import click

from dtool import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    pass
