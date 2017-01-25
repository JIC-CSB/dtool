"""Tests for dtool.archive.ArchiveFileBuilder class."""

import shutil
import tempfile

import pytest


@pytest.fixture
def tmp_dir(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d

def test_archive_header_file_order():
    from dtool.archive import ArchiveFileBuilder
    assert ArchiveFileBuilder.header_file_order == ('.dtool/dtool',
                                                    '.dtool/manifest.json',
                                                    'README.yml')

# Functional tests.

def test_ArchiveFileBuilder_from_path(tmp_dir):
    from dtool.archive import ArchiveDataSet, ArchiveFileBuilder

    archive_ds = ArchiveDataSet("my_archive")
    archive_ds.persist_to_path(tmp_dir)

    archive_builder = ArchiveFileBuilder.from_path(tmp_dir)
    assert archive_ds == archive_builder._archive_dataset

