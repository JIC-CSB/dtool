CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.


[Unreleased]
~~~~~~~~~~~~

Added
^^^^^

- dtool.archive.ArchiveFileBuilder


Changed
^^^^^^^

- dtool.archive.ArchiveFile no longer used to build archives


Deprecated
^^^^^^^^^^

Removed
^^^^^^^

Fixed
^^^^^


Security
^^^^^^^^


[0.8.0] - 2017-01-25
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- DescriptiveMetadata class
- Full DataSet class
- ArchiveDataSet class
- ArchiveFile class
- Collection class in dtool module

Changed
^^^^^^^

- *new metadata file structure (.dtool/dtool and .dtool/manifest.json)*
- *major API breaking changes*
- moved away from functional towards OO paradigm
- dtool.arctool.new_archive_dataset now uses DataSet class, always takes descriptive metadata as a parameter and returns both the dataset and the path to which it is persisted

Deprecated
^^^^^^^^^^

Removed
^^^^^^^

Fixed
^^^^^


Security
^^^^^^^^



[0.7.0] - 2017-01-16
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Datatool command line tool implementation
- DataSet initialisation and persistence
- manifest_root in .dtool-dataset

Fixed
^^^^^

- Add libmagic1 to packages installed in Docker image


[0.6.1] - 2017-01-11
~~~~~~~~~~~~~~~~~~~~

Fixed
^^^^^

- Added missing package to setup.py


[0.6.0] - 2017-01-11
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add Project class to arctool
- Add API call is_collection to test if path is collection
- Document tab completion (now enabled due to using entry point for CLI)
- Add API call icreate_collection for idempotently creating new collection.

Changed
^^^^^^^

- Change location of CLI script to use entry point.
- Change new_archive to new_archive_dataset in arctool API


[0.5.0] - 2017-01-09
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Add CLI commands for file verification
- Add API calls for single file verification and all files verification
- Add logging of dataset UUID to CLI operations
- Add logging of full command line invocation to CLI
- Archive class loaded from .tar or .tar.gz file
- DataSet class loaded from path
- Progress bar for tar creation
- API documentation

Changed
^^^^^^^

- Documentation now built using Sphinx
- Split package into modules: ``archive``, ``arctool``, ``filehasher``,
  ``manifest`` and ``slurm``


[0.4.3] - 2016-12-19
~~~~~~~~~~~~~~~~~~~~

Fixed
^^^^^

- *Added dtool_version to manifest.json*


[0.4.2] - 2016-12-17
~~~~~~~~~~~~~~~~~~~~

Fixed
^^^^^

- *Removed arctool_version from manifest.json*


[0.4.1] - 2016-12-16
~~~~~~~~~~~~~~~~~~~~

Fixed
^^^^^

- *Removed arctool_version from README.yml*
- Fixed defect where ``arctool create archive`` could not be run from arbitrary location


[0.4.0] - 2016-12-16
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- *Create .dtool-dataset with UUID, user and version*
- *Include name of hash function in manifest.json*
- Added logging of API version to CLI
- Added --version argument to CLI
- Added CLI integration tests
- Added output of next command and outside-tool actions to CLI
- Added README.yml validation upon archive creation
- Added `extract_file()` method to dtool package
- *Added "confidential" key to README.yml meta data (defaults to False)*
- *Added "personally_identifiable_information" key to README.yml meta data
  (defaults to False)*

Changed
^^^^^^^

- *Changed manifest creation to include file mimetypes from python-magic*
- *Changed tar creation to force README.yml and manifest.json to be first two files*


[0.3.0] - 2016-12-14
~~~~~~~~~~~~~~~~~~~~

- Initial tagged release
