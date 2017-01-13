"""Tests for the dtool cli."""

import subprocess


def test_version():

    cmd = ["datatool", "--version"]
    output = subprocess.check_output(cmd)
    output = output.decode('utf8')

    assert output.startswith('datatool, version')
