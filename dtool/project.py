"""Project module."""

import os

from dtool import Collection
from dtool.utils import write_templated_file


class Project(Collection):
    """Class representing a specific project.

    Writes a README.yml with the project name."""

    def __init__(self, name):
        super(Project, self).__init__()
        self.name = name

    def _safe_create_readme(self):
        if not os.path.isfile(self.abs_readme_path):
            descriptive_metadata = {'project_name': self.name}
            write_templated_file(
                self.abs_readme_path,
                'dtool_project_README.yml',
                descriptive_metadata)
