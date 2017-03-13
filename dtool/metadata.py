"""Metadata module."""

import os

import jinja2.meta
import click

from dtool.utils import write_templated_file, JINJA2_ENV


class DescriptiveMetadata(object):
    """Class for building up descriptive metadata."""

    def __init__(self, schema=None):
        if schema is None:
            self._schema = None
            self._ordered_keys = []
            self._dict = {}
        else:
            self._ordered_keys, _ = map(list, zip(*schema))
            self._dict = dict(schema)

    def __iter__(self):
        for k in self.ordered_keys:
            yield k, self._dict[k]

    def __getitem__(self, key):
        return self._dict[key]

    def keys(self):
        return self.ordered_keys

    @property
    def ordered_keys(self):
        return self._ordered_keys

    def update(self, d):
        new_keys = set(d.keys()) - set(self.keys())
        ordered_new_keys = sorted(list(new_keys))
        self._ordered_keys.extend(ordered_new_keys)
        self._dict.update(d)

    def prompt_for_values(self):
        for key, default in self:
            self._dict[key] = click.prompt(key, default=default)

    def persist_to_path(
            self, path, filename='README.yml', template="base.yml.j2"):
        """Write the metadata to path + filename."""

        output_path = os.path.join(path, filename)

        # Find variables in the template from the abstract syntax tree (ast).
        template_source = JINJA2_ENV.loader.get_source(JINJA2_ENV, template)
        ast = JINJA2_ENV.parse(template_source)
        template_variables = jinja2.meta.find_undeclared_variables(ast)

        # Create yaml for any variables that are not present in the template.
        extra_variables = set(self.keys()) - template_variables
        extra_yml_content = ["{}: {}".format(k, self[k])
                             for k in self.ordered_keys
                             if k in extra_variables]

        # Create the dictionary to pass to the template.
        variables = self._dict.copy()
        variables["extra_yml_content"] = extra_yml_content

        write_templated_file(output_path, template, variables)
