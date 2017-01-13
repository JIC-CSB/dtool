"""Manage datasets."""

import sys
import json
import getpass

import click

from fluent import sender

from dtool import __version__
from dtool.arctool import create_manifest

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
