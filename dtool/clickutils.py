"""dtool utilities for making command line interfaces."""

import os

import click

from dtool import Project


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