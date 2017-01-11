#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

__version__ = "0.6.1"

VERBOSE = True


def log(message):
    """Log a message.

    :param message: message to be logged
    """
    if VERBOSE:
        print(message)
