"""Helper functions for the arctool command line tool."""

import yaml


def parse_config(fpath):
    """Return a dictionary with a user's settings."""
    with open(fpath, "r") as fh:
        config = yaml.load(fh)
    return config
