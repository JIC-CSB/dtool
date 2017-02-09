"""dtool utilities for making command line interfaces."""

import os

import click

from dtool import (
    Project,
    DescriptiveMetadata,
    metadata_from_path,
    _DtoolObject,
    NotDtoolObject,
)
from dtool.utils import auto_metadata


def create_project(path):
    """Create new project if it does not exist in path, prompting
    the user for a project name and creating the directory.

    A project is a :class:`dtool.Project`."""

    path = os.path.abspath(path)

    project_name = click.prompt('project_name',
                                default='my_project')

    project = Project(project_name)
    project_dir = os.path.join(path, project_name)
    os.mkdir(project_dir)
    project.persist_to_path(project_dir)

    click.secho('Created new project in: ', nl=False)
    click.secho(project_dir, fg='green')

    return project


def generate_descriptive_metadata(schema, parent_path):
    descriptive_metadata = DescriptiveMetadata(schema)
    descriptive_metadata.update(auto_metadata("nbi.ac.uk"))
    descriptive_metadata.update(metadata_from_path(parent_path))
    descriptive_metadata.prompt_for_values()

    return descriptive_metadata


def info_from_path(path):
    """Return information string about the path.

    Is it a dtool dataset or collection or not a dtool object?

    :param path: path to a directory of interest
    :raises: OSError if path is not a directory
    :returns: information string
    """
    if not os.path.isdir(path):
        raise(OSError("Not a directory: {}".format(path)))
    try:
        dtool_object = _DtoolObject.from_path(path)
    except NotDtoolObject:
        return "Directory is not a dtool object"
    return "Directory is a dtool {}".format(
        dtool_object._admin_metadata["type"])
