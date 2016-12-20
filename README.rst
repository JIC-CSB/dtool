dtool - manage JIC archive data
===============================

.. image:: https://travis-ci.org/JIC-CSB/dtool.svg?branch=master
    :target: https://travis-ci.org/JIC-CSB/dtool

.. image:: https://codecov.io/github/JIC-CSB/dtool/coverage.svg?branch=master
   :target: https://codecov.io/github/JIC-CSB/dtool?branch=master
   :alt: Code Coverage


Overview
--------

The dtool project project provides tools for managing (scientific) data.
It aims to help in three areas:

1. Adding structure and meta data to your project and files
2. Verifying the integrity of the files in your project
3. Creating archives for long term storage


Design philosophy
-----------------

The tools in this project should produce outputs that can be understood without
access to these tools. This is important as it is likely that the outputs of
from these tools may outlive these tools.


What the tools in this project do
---------------------------------

1. Provides templates for meta data associated with a project in the plain
   text yaml file format
2. Provides a means to generate a manifest with meta data for all files in
   a data directory
3. Provides directory structure templates for archiving data
4. Provides wrappers to create tar archives
5. Provides wrappers to gzip tar archives
6. Provides wrappers to verify the integrity of files in gzipped tar archives


Usage
-----

arctool
~~~~~~~

Warning: this section of the documentation assumes functionality that will be
added in a future release.

``arctool`` is a tool for archiving data.

First you will need to create an archiving staging area.

::

    $ mkdir archive_staging_area
    $ cd archive_staging_area

To start building an archive use ``arctool new``, this will create a directory structure
in the working directory (``archive_staging_area``) and prompt you to specify some meta
data associated with the project.

::

    $ archtool new

    # Add ouput here

This results in the directory structure below.

::

    $ tree some_project

    # Add output here

Inspect and extend the ``some_project/data_set_1/README.yml`` as necessary.
This file is meant to provide overall meta data of the data set.

::

    $ cat some_project/data_set_1/README.yml

    # Add output here

Move your data to be archived into the ``some_project/data_set_1/archive``
directory.

::

    $ mv ~/my_old_project/data_set_1/* some_project/data_set_1/archive/

Generate meta data for the files that you just moved into the
``some_project/data_set_1/archive`` directory.

::

    $ arctool manifest create some_project/data_set_1/archive

This will generate a ``some_project/data_set_1/manifest.json`` file.

::

    $ head some_project/data_set_1/manifest.json

    # Add output here

Create a tar ball of the data set.

::

    $ arctool archive create some_project/data_set_1

    # Add output here

Compress the archive using gzip compression.

::

    $ arctool archive compress some_project/data_set_1

    # Add output here

Finally move the gzipped tarball archive into your long term storage.


Installation
------------

::

    $ git clone https://github.com/JIC-CSB/dtool.git
    $ cd dtool
    $ python setup.py install


Deployment
----------

1. Build Docker image
2. Build Singularity image from Docker image
3. Copy Singularity image to cluster

Development
-----------

The testing framework makes use of tox.
Install tox using ``pip``::

    pip install tox

Run the test suite using the command::

    tox
