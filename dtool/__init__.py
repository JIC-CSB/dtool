#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json
import hashlib
import subprocess

VERBOSE = True


def log(message):

    if VERBOSE:
        print(message)


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
    """Return archive manfifest data structure.

    Structure includes all files in the filesystem rooted at path with:

    * Relative path
    * SHA1 hash
    * Last modification time
    * Size

    """

    full_file_list = generate_full_file_list(path)

    log('Building manifest')
    entries = []
    for n, filename in enumerate(full_file_list):
        log('Processing ({}/{}) {}'.format(1+n, len(full_file_list), filename))
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

    manifest = dict(file_list=entries)

    return manifest


def generate_full_file_list(path):
    """Return a list of fully qualified paths to all files in directories under
    the given path."""

    file_list = []

    # FIXME - platform dependency
    log('Generating file list')
    if path[-1] == '/':
        path_length = len(path)
    else:
        path_length = 1 + len(path)

    for dirpath, dirnames, filenames in os.walk(path):
        for fn in filenames:
            relative_path = os.path.join(dirpath, fn)
            file_list.append(relative_path[path_length:])

    return file_list


def create_manifest(args):

    archive_root_path, _ = os.path.split(args.data_path)
    manifest_filename = os.path.join(archive_root_path, 'manifest.json')

    manifest_data = generate_manifest(args.data_path)

    with open(manifest_filename, 'w') as f:
        json.dump(manifest_data, f, indent=4)


def create_archive(args):

    archive_name = 'arc.tar'

    tar_command = ['tar', '-cvf', os.path.join('..', archive_name), '.']
    subprocess.call(tar_command, cwd=args.data_path)

    gzip_command = ['gzip', archive_name]
    subprocess.call(gzip_command)
