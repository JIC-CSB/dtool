"""Test filehasher API."""

import os

HERE = os.path.dirname(__file__)
TEST_INPUT_DATA = os.path.join(HERE, "data", "basic", "input")


def test_shasum():
    from dtool.filehasher import shasum
    expected = "a250369afb3eeaa96fb0df99e7755ba784dfd69c"
    test_file = os.path.join(TEST_INPUT_DATA, 'archive', 'file1.txt')
    actual = shasum(test_file)
    assert actual == expected


def test_FileHasher():
    from dtool.filehasher import FileHasher

    def dummy():
        pass

    file_hasher = FileHasher(dummy)
    assert file_hasher.name == "dummy"


def test_generate_file_hash():
    from dtool.filehasher import generate_file_hash
    assert generate_file_hash.name == "shasum"