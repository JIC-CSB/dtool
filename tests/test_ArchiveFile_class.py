"""Tests for dtool.archive.ArchiveFile class."""


def test_archive_header_file_order():

    from dtool.archive import ArchiveFile

    assert ArchiveFile.header_file_order == ('.dtool/dtool',
                                             '.dtool/manifest.json',
                                             'README.yml')
