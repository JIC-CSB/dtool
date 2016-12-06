"""Tests for dtool."""

import os
import json

TEST_INPUT_DATA = 'test_data/input'
TEST_OUTPUT_DATA = 'test_data/output'

def test_shasum():

    from dtool import shasum

    expected = "a250369afb3eeaa96fb0df99e7755ba784dfd69c"

    test_file = os.path.join(TEST_INPUT_DATA, 'archive', 'file1.txt')
    actual = shasum(test_file)

    assert actual == expected

def test_generate_manifest():

    from dtool import generate_manifest

    expected_manifest_file = os.path.join(TEST_OUTPUT_DATA, 'raw_manifest.json')
    with open(expected_manifest_file) as fh:
        expected = json.load(fh)

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_manifest(test_archive_path)

    assert(actual == expected)

def test_generate_full_file_list():

    from dtool import generate_full_file_list

    expected = ['file1.txt', 'dir1/file2.txt']

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_full_file_list(test_archive_path)

    assert sorted(actual) == sorted(expected)

def test_generate_archive_manifest():

    from dtool import generate_archive_manifest

    expected_manifest_file = os.path.join(TEST_OUTPUT_DATA, 'manifest.json')
    with open(expected_manifest_file) as fh:
        expected = json.load(fh)

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_archive_manifest(test_archive_path)

    assert actual == expected