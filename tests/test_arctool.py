"""Tests arctool functionality."""

import os
import tempfile
import shutil

from pytest import fixture

CONFIG_TEXT = """---
owner_name: Tjelvar Olsson
owner_email: tjelvar.olsson@jic.ac.uk
owner_unix_username: olssont
archive_staging_area: ~/archive_staging_area
"""


@fixture
def tmp_conf_path(request):
    d = tempfile.mkdtemp()
    conf_path = os.path.join(d, ".arctool.yml")
    with open(conf_path, "w") as fh:
        fh.write(CONFIG_TEXT)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    return conf_path


def test_parse_config(tmp_conf_path):
    from dtool.arctool import parse_config
    conf = parse_config(tmp_conf_path)
    assert conf["owner_name"] == "Tjelvar Olsson"
    assert conf["owner_email"] == "tjelvar.olsson@jic.ac.uk"
    assert conf["owner_unix_username"] == "olssont"
    assert conf["archive_staging_area"] == "~/archive_staging_area"



