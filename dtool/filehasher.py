"""Module for generating file hashes."""

import hashlib


class FileHasher(object):
    """Class for associating hash functions with names."""

    def __init__(self, hash_func):
        self.func = hash_func
        self.name = hash_func.__name__

    def __call__(self, filename):
        return self.func(filename)


def shasum(filename):
    """Return hex digest of SHA-1 hash of file.

    :param filename: path to file
    :returns: shasum of file
    """

    # Tried using Mac native shasum. But this was slower.
    # Maybe not surprising as shasum on Mac was a Perl script,
    # i.e. not a compiled binary.

    BUF_SIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as f:
        buf = f.read(BUF_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BUF_SIZE)

    return hasher.hexdigest()


generate_file_hash = FileHasher(shasum)
