"""dtool utilities."""

from jinja2 import Environment, PackageLoader


def write_templated_file(path, template_name, variables):
    """Load the template given by template_name, render it with
    variables and write it to path.

    :param path: Path to file to which template will be written
    :param template_name: Name of template to use
    :param variables: Dict containing variables to be templated
    """

    env = Environment(loader=PackageLoader('dtool', 'templates'),
                      keep_trailing_newline=True)
    template = env.get_template(template_name)

    with open(path, 'w') as fh:
        fh.write(template.render(variables))
