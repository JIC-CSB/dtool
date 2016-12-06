#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os

def generate_manifest(path):
    """Return archive data structure.

    Structure includes all files in the filesystem rooted at path with:

    * Relative path
    * SHA1 hash
    * Last modification time
    * Size

    """

def generate_full_file_list(path):
    """Return a list of fully qualified paths to all files in directories under
    the given path."""

    file_list = []

    path_length = 1 + len(path)
    
    for dirpath, dirnames, filenames in os.walk(path):
        for fn in filenames:
            relative_path = os.path.join(dirpath, fn)
            file_list.append(relative_path[path_length:])

    return file_list