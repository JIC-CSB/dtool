#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import hashlib
import argparse

def shasum(filename):
    """Return hex digest of SHA-1 hash of file."""

    BUF_SIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read(BUF_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BUF_SIZE)

    return hasher.hexdigest()

def generate_manifest(path):
    """Return manfifest data structure.

    Structure includes all files in the filesystem rooted at path with:

    * Relative path
    * SHA1 hash
    * Last modification time
    * Size

    """

    full_file_list = generate_full_file_list(path)

    entries = []
    for filename in full_file_list:
        fq_filename = os.path.join(path, filename)
        st_size = os.stat(fq_filename).st_size
        st_mtime = os.stat(fq_filename).st_mtime
        file_hash = shasum(fq_filename)

        entry = {}
        entry['path'] = filename
        entry['hash'] = file_hash
        entry['size'] = st_size
        entry['mtime'] = st_mtime
        entries.append(entry)

    return entries

def generate_archive_manifest(path):
    """Return archive data structure.

    This is a file manifest (see generate_manifest) rooted at the 'archive'
    level.
    """

    raw_manifest = generate_manifest(path)

    for entry in raw_manifest:
        filename = entry['path']
        archive_filename = os.path.join('archive', filename)
        entry['path'] = archive_filename

    return raw_manifest 

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

def create_archive_manifest():

    pass

def main():

    parser = argparse.ArgumentParser(__doc__)  

    

if __name__ == "__main__":
    main()