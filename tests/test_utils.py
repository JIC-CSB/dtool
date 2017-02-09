"""Tests for dtool utils."""

import os

import yaml

from . import tmp_dir_fixture  # NOQA


def test_write_templated_file(tmp_dir_fixture):  # NOQA
    from dtool.utils import write_templated_file

    expected_templated_file = os.path.join(tmp_dir_fixture, 'README.yml')

    assert not os.path.isfile(expected_templated_file)

    variables = dict([
        ("project_name", u"my_project"),
        ("dataset_name", u"brassica_rnaseq_reads"),
        ("confidential", False),
        ("personally_identifiable_information", False),
        ("owner_name", u"Your Name"),
        ("owner_email", u"your.email@example.com"),
        ("unix_username", u"namey"),
        ("date", u"2017-01-01"),
    ])
    write_templated_file(expected_templated_file,
                         'dtool_dataset_README.yml',
                         variables)

    assert os.path.isfile(expected_templated_file)

    with open(expected_templated_file) as fh:
        parsed_file = yaml.load(fh)

    for check_var in ['project_name',
                      'dataset_name',
                      'confidential']:
        assert parsed_file[check_var] == variables[check_var]

    assert str(parsed_file['creation_date']) == variables['date']


def test_auto_metadata_generation():
    from dtool.utils import auto_metadata
    import datetime
    import getpass

    username = getpass.getuser()
    email = username + "@example.com"
    assert auto_metadata("example.com") == \
        {"date": str(datetime.date.today()),
         "owner_username": username,
         "owner_email": email}
