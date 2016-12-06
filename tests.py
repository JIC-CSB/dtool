"""Tests for dtool."""

import os
import json

TEST_INPUT_DATA = 'test_data/input'
TEST_OUTPUT_DATA = 'test_data/output'

def test_generate_manifest():

    from dtool import generate_manifest

    expected_manifest_file = os.path.join(TEST_OUTPUT_DATA, 'manifest.json')
    with open(expected_manifest_file) as fh:
        expected = json.load(fh)

    test_archive_path = os.path.join(TEST_INPUT_DATA, 'archive')
    actual = generate_manifest(test_archive_path)

    actual == expected