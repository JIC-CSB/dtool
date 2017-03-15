"""Tests for dtool."""

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


def test_version_is_str():
    from dtool import __version__
    assert isinstance(__version__, str)
