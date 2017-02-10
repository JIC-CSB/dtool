"""Test the :class:`dtool.Manifest` class."""

import os
import json
import shutil

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATASET


def test_manifest_functional(tmp_dir_fixture):  # NOQA
    from dtool import Manifest
    from dtool.filehasher import shasum

    data_path = os.path.join(TEST_SAMPLE_DATASET, "data")
    manifest = Manifest(data_path, shasum)

    hashes = [entry["hash"] for entry in manifest["file_list"]]
    assert "290d3f1a902c452ce1c184ed793b1d6b83b59164" in hashes

    output_fpath = os.path.join(tmp_dir_fixture, "manifest.json")
    assert not os.path.isfile(output_fpath)

    manifest.persist_to_path(output_fpath)
    assert os.path.isfile(output_fpath)

    with open(output_fpath) as fh:
        manifest_from_json = json.load(fh)
    assert manifest == manifest_from_json


def test_manifest_initialisation():
    from dtool import Manifest, __version__
    from dtool.filehasher import md5sum

    data_path = os.path.join(TEST_SAMPLE_DATASET, "data")

    manifest = Manifest(
        abs_manifest_root=data_path, hash_func=md5sum)

    assert manifest.abs_manifest_root == data_path
    assert manifest.hash_generator.name == "md5sum"

    assert isinstance(manifest, dict)
    assert "file_list" in manifest
    assert "dtool_version" in manifest
    assert "hash_function" in manifest

    assert isinstance(manifest["file_list"], list)
    assert manifest["dtool_version"] == __version__
    assert manifest["hash_function"] == "md5sum"

    assert len(manifest["file_list"]) == 7

    hashes = [entry["hash"] for entry in manifest["file_list"]]
    assert "cced2acdb7392ee8c13867f52f2a44b1" in hashes


def test_regenerate_file_list(tmp_dir_fixture):  # NOQA
    from dtool import Manifest
    from dtool.filehasher import shasum

    input_data_path = os.path.join(TEST_SAMPLE_DATASET, "data")
    output_data_path = os.path.join(tmp_dir_fixture, "data")
    shutil.copytree(input_data_path, output_data_path)

    manifest = Manifest(output_data_path, shasum)
    assert len(manifest["file_list"]) == 7

    # Remove all the files from the manifest root directory.
    shutil.rmtree(output_data_path)
    os.mkdir(output_data_path)

    manifest.regenerate_file_list()
    assert len(manifest["file_list"]) == 0


def test_persist_to_path(tmp_dir_fixture):  # NOQA

    from dtool import Manifest, __version__
    from dtool.filehasher import shasum

    manifest = Manifest(tmp_dir_fixture, shasum)

    output_fpath = os.path.join(tmp_dir_fixture, "manifest.json")
    assert not os.path.isfile(output_fpath)

    manifest.persist_to_path(output_fpath)
    assert os.path.isfile(output_fpath)

    with open(output_fpath) as fh:
        manifest_from_json = json.load(fh)

    assert manifest_from_json["dtool_version"] == __version__
    assert manifest_from_json["hash_function"] == "shasum"
    assert len(manifest_from_json["file_list"]) == 0
