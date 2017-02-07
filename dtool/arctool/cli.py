#!/usr/bin/env python
"""Manage archiving of data."""

import sys
import os
import getpass

import click

from dtool import (
    __version__,
    DataSet,
    Project,
    DtoolTypeError,
    NotDtoolObject,
)
from dtool.arctool import (
    README_SCHEMA,
    readme_yml_is_valid,
    new_archive_dataset,
)
from dtool.archive import (
    ArchiveDataSet,
    ArchiveFile,
    ArchiveFileBuilder,
    compress_archive,
)
from dtool.slurm import generate_slurm_script
from dtool.clickutils import create_project, generate_descriptive_metadata

from fluent import sender

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


@cli.group(invoke_without_command=True)
@click.pass_context
@click.option('--staging_path',
              help='Path to staging area where new project will be created',
              default='.',
              type=click.Path(exists=True))
def new(ctx, staging_path):

    # ctx is passed in via @click.pass_context

    # Makes default behaviour for 'arctool new' be create dataset
    if ctx.invoked_subcommand is None:
        try:
            project = Project.from_path(staging_path)
            project_path = staging_path
        except NotDtoolObject:
            project = create_project(staging_path)
            project_path = os.path.join(staging_path, project.name)
        except DtoolTypeError:
            raise(click.UsageError("Don't create a project in a dataset"))

        cli_new_dataset(project_path)


@new.command()
@click.option('--staging_path',
              help='Path to staging area where new project will be created',
              default='.',
              type=click.Path(exists=True))
def project(staging_path):

    create_project(staging_path)


@new.command()
@click.option('--staging_path',
              help='Path to staging area where new archive will be created',
              default='.',
              type=click.Path(exists=True))
def dataset(staging_path):

    cli_new_dataset(staging_path)


def cli_new_dataset(staging_path):
    staging_path = os.path.abspath(staging_path)

    click.secho('Starting new archive in: ', nl=False)
    click.secho(staging_path, fg='green')

    logger.emit('pre_new_archive', {'staging_path': staging_path})

    descriptive_metadata = generate_descriptive_metadata(
        README_SCHEMA, staging_path)

    dataset, dataset_path, readme_path = new_archive_dataset(
        staging_path, descriptive_metadata)

    click.secho('Created new archive in: ', nl=False)
    click.secho(dataset_path, fg='green')

    log_data = {'metadata': descriptive_metadata,
                'archive_path': dataset_path,
                'dataset_uuid': dataset.uuid}
    logger.emit('new', log_data)

    archive_data_path = os.path.join(dataset_path, dataset.data_directory)
    click.secho('Now:')
    click.secho('  1. Edit {}'.format(readme_path), fg='yellow')
    click.secho('  2. Move archive data into {}'.format(archive_data_path),
                fg='yellow')
    click.secho('Then: ', nl=False)
    click.secho('arctool manifest create {}'.format(dataset_path),
                fg='cyan')


@cli.group()
def manifest():
    pass


@manifest.command()
@click.argument('path', 'Path to archive dataset directory.',
                type=click.Path(exists=True))
def create(path):

    archive_dataset = ArchiveDataSet.from_path(path)

    log_data = {'uuid': archive_dataset.uuid, 'path': path}
    logger.emit('pre_create_manifest', log_data)

    archive_dataset.update_manifest()

    click.secho('Created manifest', fg='green')

    log_data = {'uuid': archive_dataset.uuid,
                'manifest': archive_dataset.manifest}
    logger.emit('post_create_manifest', log_data)

    click.secho('Next: ', nl=False)
    click.secho('arctool archive create {}'.format(path), fg='cyan')


@cli.group()
def archive():
    pass


@archive.command()  # NOQA
@click.argument('path', 'Path to dataset directory.',
                type=click.Path(exists=True))
def create(path):
    path = os.path.abspath(path)

    dataset = DataSet.from_path(path)
    log_data = {'path': path,
                'dataset_uuid': dataset.uuid}
    logger.emit('pre_create_archive', log_data)

    readme_path = dataset.abs_readme_path
    click.secho('Validating readme at: ', nl=False)
    click.secho(readme_path, fg='green')
    readme_str = open(readme_path, "r").read()
    if not readme_yml_is_valid(readme_str):
        click.secho("Not valid", fg='red')
        sys.exit(2)

    archive_builder = ArchiveFileBuilder.from_path(path)
    hacked_path = os.path.join(path, "..")
    tar_file_path = archive_builder.persist_to_tar(hacked_path)

#   tar_file_path = dtool.arctool.initialise_archive(path)

#   def show_func(item):
#       if item is None:
#           return ''
#       return str(item['path'])

#   with click.progressbar(manifest_filedict,
#                          length=tot_size,
#                          item_show_func=show_func) as bar:
#       for entry in bar:
#           rpath = os.path.join('archive', entry['path'])
#           append_to_tar_archive(path, rpath)
#           bar.update(entry['size'])

    click.secho('Archiving data at: ', nl=False)
    click.secho(path, fg='green')

    click.secho('Created archive: ', nl=False)
    click.secho(tar_file_path, fg='green')

    archive_size = os.stat(tar_file_path).st_size
    post_tar_log = {'dataset_uuid': dataset.uuid,
                    'archive_size': archive_size,
                    'output_tar_path': tar_file_path}
    logger.emit('post_create_archive', post_tar_log)

    click.secho('Next: ', nl=False)
    click.secho('arctool archive compress {}'.format(tar_file_path), fg='cyan')


@archive.command()
@click.option('--cores', '-c', default=4, help='Number of CPU cores to use.')
@click.option('--slurm', '-s', is_flag=True, default=False,
              help='Rather than running compression, generate SLURM script.')
@click.argument('path', 'Path to uncompressed archive (tar) file.',
                type=click.Path(exists=True))
def compress(path, cores, slurm):
    path = os.path.abspath(path)
    archive = ArchiveFile.from_file(path)

    if not slurm:
        click.secho('Compressing archive: ', nl=False)
        click.secho(path, fg='green')

        pre_log = {'dataset_uuid': archive.admin_metadata["uuid"],
                   'archive_path': path,
                   'cores': cores,
                   'tar_size': os.stat(path).st_size}
        logger.emit('pre_compress_archive', pre_log)

        compressed_archive_path = compress_archive(path, n_threads=cores)

        click.secho('Created compressed file: ', nl=False)
        click.secho(compressed_archive_path, fg='green')

        post_log = {'dataset_uuid': archive.admin_metadata["uuid"],
                    'compressed_archive_path': compressed_archive_path,
                    'gzip_size': os.stat(compressed_archive_path).st_size}
        logger.emit('post_compress_archive', post_log)

        click.secho('Now:')
        click.secho('  Move {} to archive storage'.format(
            compressed_archive_path), fg='yellow')

    # WARNING - be VERY careful automating this to submit the job - if the
    # logic fails, the job will repeatedly submit itself forever!
    else:
        job_parameters = dict(n_cores=cores, partition="rg-sv")
        command_string = "arctool archive compress -c {} {}".format(cores,
                                                                    path)

        submit_string = generate_slurm_script(command_string, job_parameters)

        print(submit_string)


@cli.group()
def verify():
    pass


@verify.command()
@click.argument('path', 'Path to compressed archive.',
                type=click.Path(exists=True))
def summary(path):
    archive_file = ArchiveFile.from_file(path)
    summary_data = archive_file.summarise()

    size_in_gibi = float(summary_data['total_size']) / (2 ** 30)

    click.secho("Archive contains", nl=False)
    click.secho(" {} ".format(summary_data['n_files']), fg='green', nl=False)
    click.secho("files.")

    click.secho("Total uncompressed archive size is", nl=False)
    click.secho(" {:.2f} GiB".format(size_in_gibi), fg='green', nl=False)
    click.secho(".")


@verify.command()
@click.argument('path', 'Path to compressed archive.',
                type=click.Path(exists=True))
def full(path):

    click.secho("Performing full verification on:", nl=False)
    click.secho(" {}".format(path), fg='green')

    archive_file = ArchiveFile.from_path(path)
    result = archive_file.verify_all()

    click.secho("Verification ", nl=False)
    if result:
        click.secho("passed", fg='green')
    else:
        click.secho("failed", fg='red')


if __name__ == "__main__":
    cli()
