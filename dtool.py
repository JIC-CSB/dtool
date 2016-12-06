#!/usr/bin/env python2
"""Tool for managing JIC archive data."""

import os
import json
import hashlib
import argparse
import subprocess

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

    manifest = { "file_list" : entries }

    return manifest

def generate_full_file_list(path):
    """Return a list of fully qualified paths to all files in directories under
    the given path."""

    file_list = []

    # FIXME - platform dependency
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

def main():

    parser = argparse.ArgumentParser(description=__doc__)

    subparsers = parser.add_subparsers(help='sub-command help', 
                                        dest='subparser_name')

    parser_manifest = subparsers.add_parser('manifest', help='Manage data manifest')
    manifest_subparsers = parser_manifest.add_subparsers()
    parser_manifest_create = manifest_subparsers.add_parser('create', help='Create data manifest')
    parser_manifest_create.set_defaults(func=create_manifest)
    parser_manifest_create.add_argument('data_path', help='Path to data')

    parser_archive = subparsers.add_parser('archive', help='Manage data archive')
    archive_subparsers = parser_archive.add_subparsers()
    parser_archive_create = archive_subparsers.add_parser('create', help='Create data archive')
    parser_archive_create.set_defaults(func=create_archive)
    parser_archive_create.add_argument('data_path', help='Path to data')

    args = parser.parse_args()

    args.func(args)
    

if __name__ == "__main__":
    main()