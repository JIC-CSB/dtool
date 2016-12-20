CHANGELOG
=========

Unreleased
~~~~~~~~~~

- Split package into modules: ``archive``, ``arctool``, ``filehasher``,
  ``manifest`` and ``slurm``


0.4.3
~~~~~

- *Added dtool_version to manifest.json*

0.4.2
~~~~~

- *Removed arctool_version from manifest.json*


0.4.1
~~~~~

- *Removed arctool_version from README.yml*
- Fixed defect where ``arctool create archive`` could not be run from arbitrary location


0.4.0
~~~~~

- *Create .dtool-dataset with UUID, user and version*
- *Include name of hash function in manifest.json*
- *Changed manifest creation to include file mimetypes from python-magic*
- Added CLI integration tests
- *Changed tar creation to force README.yml and manifest.json to be first two files*
- Added logging of API version to CLI
- Added --version argument to CLI
- Added output of next command and outside-tool actions to CLI
- Added README.yml validation upon archive creation
- *Added "confidential" key to README.yml meta data (defaults to False)*
- *Added "personally_identifiable_information" key to README.yml meta data
  (defaults to False)*
- Added `extract_file()` method to dtool package


0.3.0
~~~~~

- Initial tagged release
