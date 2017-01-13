"""Tests for the dtool cli."""

import subprocess

import pytest

def test_version():

    cmd = ["datatool", "--version"]
    output = subprocess.check_output(cmd)

    assert output.startswith('datatool, version')


