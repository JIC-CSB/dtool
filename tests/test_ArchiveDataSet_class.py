"""Tests for dtool.archive.ArchiveDataSet class."""

def test_ArchiveDataSet_initialisation():
    from dtool.archive import ArchiveDataSet
    archive_ds = ArchiveDataSet(name="my_archive")
    assert archive_ds.name == "my_archive"
    assert archive_ds.data_directory == "archive"
