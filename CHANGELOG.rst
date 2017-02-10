CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.


[Unreleased]
~~~~~~~~~~~~

Added
^^^^^

- ``dtool info`` CLI command
- ``dtool.clickutils.info_from_path`` function
- ``dtool.DataSet.item_path_from_hash`` method
- ``dtool.filehasher.md5sum`` function


Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^

- Fluentd logging
- ``dtool.slurm`` module moved into ``arctool`` package


Fixed
^^^^^


Security
^^^^^^^^


[0.11.0] - 2017-09-17
~~~~~~~~~~~~~~~~~~~~~

Changed
^^^^^^^

- ``arctool`` - this now lives in it's own repository
   `github.com/JIC-CSB/arctool <https://github.com/JIC-CSB/arctool>`_.
- ``datatool`` CLI renamed to ``dtool``
- ``dtool.datatool.cli`` module renamed ``dtool.cli``


Removed
^^^^^^^

- The ``arctool`` CLI
- The ``dtool.archive`` and ``dtool.arctool`` modules


[0.10.0] - 2017-02-07
~~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- Extra variables from collections/projects are now propagated to the
  descriptive metadata of the dataset/archive when using the
  ``datatool``/``arctool`` CLI
- ``datatool markup`` CLI command
- ``dtool.metadata_from_path`` helper function

Changed
^^^^^^^

- datatool and arctool CLIs now use utility functions for new dataset and markup

Fixed
^^^^^

- Reading of project level metadata in ``arctool new dataset``
- Pretty printing of manifest.json (indent 2)
- Remove cookiecutter dependency
- datatool README_SCHEMA


[0.9.0] - 2017-01-27
~~~~~~~~~~~~~~~~~~~~

Added
^^^^^

- ``arctool manifest create`` (points at dataset directory)
- ``datatool new dataset`` now derives descriptive metadata defaults from parent collections/projects
- Recursive build up of descriptive metadata from parent directories
- Ability to create projects using the ``datatool``
- dtool.DescriptiveMetadata.persist_to_path method
- dtool.archive.ArchiveFileBuilder


Changed
^^^^^^^

- Now need to create ``datatool manifest update`` at dataset dir
- Move summarise_archive function into dtool.archive.ArchiveFile.summarise method
- Move verify_file and verify_all into dtool.archive.ArchiveFile class
- dtool.archive.ArchiveFile no longer used to build archives

Removed
^^^^^^^

- Ability to extract files from (gzipped) tarball using the arctool cli
- arctool.create_manifest function
- arctool.rel_paths_for_archiving
- ``datatool manifest create``

Fixed
^^^^^

- Fixed command line tools; broken because they still used create_manifest function


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
