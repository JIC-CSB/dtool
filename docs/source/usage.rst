Usage
=====

Overview
--------

The ``dtool`` command line tool allows the user to annotate data with
structural information as well as descriptive metadata.  The annotated data
will from now on be referred to as a "dataset".

There are two main workflows:

1. Creating a new dataset from scratch
2. Marking up an existing directory containing data as a dataset

As well as the concept of a dataset the ``dtool`` command line tool has the
concept of a "project". A project is simply a directory with some descriptive
metadata. When creating datasets in a project directory the descriptive
metadata of the project is automatically included into the dataset's
descriptive metadata. This is useful as it can avoid having to re-enter
metadata shared between datasets.


Walkthrough
-----------

Installing or load the tool
^^^^^^^^^^^^^^^^^^^^^^^^^^^

JIC users can load the ``dtool`` program on the cluster using the commands below.

.. code-block:: none

    $ source /common/software/linuxbrew/Cellar/lmod/5.9.3/lmod/5.9.3/init/bash
    $ module use /common/modulefiles/Core
    $ module load dtool

To install the tool manually see :doc:`installation_notes`.


Creating a new project
^^^^^^^^^^^^^^^^^^^^^^

This example creates a project directory called ``brassica_yields``
in the working directory.

.. code-block:: none

    $ dtool new project
    project_name [my_project]: brassica_yields
    Created new project in: /usr/users/JIC_a5/olssont/brassica_yields

Note also that the file ``brassica_yields/README.yml`` has been created.

.. code-block:: none

    $ cat brassica_yields/README.yml
    ---

    project_name: brassica_yields

.. note:: More information about the YAML file format can be found
          on the official website `www.yaml.org/ <http://www.yaml.org/>`_.
          For a quick guide have a look at
          `www.yaml.org/start.html <http://www.yaml.org/start.html>`_.


Add descriptive metadata to the project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To minimise repetition we can define descriptive metadata common
to all datasets at the project level. These are then propagated
to the datasets upon their creation.

For example one could update the ``brassica_yields/README.yml``
to like like the below.

.. code-block:: yaml

    ---

    project_name: brassica_yields
    owner_name: Tjelvar Olsson
    species: Brassica napus

In the above the ``owner_name`` is a *magic* key that is understood
by the dataset's metadata template. However, the ``species`` is a
key which the dataset's metadata template has no explicit understanding
of.

Creating a new dataset
^^^^^^^^^^^^^^^^^^^^^^

To create a dataset in the project we ``cd`` into the project.

.. code-block:: none

    $ cd brassica_yields/

Below we create a dataset for the wild-type data.

.. code-block:: none

    $ dtool new dataset
    project_name [brassica_yields]:
    dataset_name [dataset_name]: wt
    confidential [False]:
    personally_identifiable_information [False]:
    owner_name [Tjelvar Olsson]:
    owner_email [olssont@nbi.ac.uk]:
    owner_username [olssont]:
    date [2017-02-24]:
    species [Brassica napus]:

In the above all defaults were accepted except the ``dataset_name``.
The ``owner_name`` is always prompted for, in this case the default
value came from the project's descriptive metadata (defined in the
section above). The ``species`` was only prompted for because it
was specified in the project's metadata.

This creates the directory structure below.

.. code-block:: none

    $ tree wt/
    wt/
    ├── data
    └── README.yml

Below is the content of the dataset's descriptive metadata contained
in ``wt/README.yml``.

.. code-block:: none

    $ cat wt/README.yml
    ---

    project_name: brassica_yields
    dataset_name: wt
    confidential: False
    personally_identifiable_information: False
    owners:
      - name: Tjelvar Olsson
        email: olssont@nbi.ac.uk
        username: olssont
    creation_date: 2017-02-24
    species: Brassica napus
    # links:
    #  - http://doi.dx.org/your_doi
    #  - http://github.com/your_code_repository
    # budget_codes:
    #  - E.g. CCBS1H10S

.. note:: One can edit this file to add more descriptive metadata.
          Suggested items such as ``links`` and ``budget_codes``
          are included in the comments at the end.

Adding data
^^^^^^^^^^^

At this point one would start moving the raw data into the
``wt/data`` directory.

For the purposes of this we will just create a small FASTA
file in there.

.. code-block:: none

    $ cat > wt/data/sequence.fasta
    > Brassica napus wild-type
    ATAACCGA


Updating the structural information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Structural information about the data in the dataset is
stored in a so called "manifest". Once the data has been
added to the ``wt/data`` directory one needs to update
the manifest.

.. code-block:: none

    $ dtool manifest update wt
    Updated manifest

In the above the last argument is the name of the dataset directory whose
manifest one wants to update.

At the moment there is no way of making use of the data in
the manifest using the ``dtool`` command line tool. However,
the data is stored in the file ``.dtoo/manifest.json`` so
one can view it.

.. code-block:: none

    $ cat wt/.dtool/manifest.json
    {
      "file_list": [
        {
          "size": 36,
          "path": "sequence.fasta",
          "mtime": 1487935747.8634017,
          "mimetype": "text/plain",
          "hash": "acd78986dc32264fd3de1b7865254b6450e60124"
        }
      ],
      "hash_function": "shasum",
      "dtool_version": "0.12.1"
    }

The :mod:`dtool` python API does provide access to the manifest.


Marking up an existing directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If data is already organised for programmatic access one
may not want to move it into a ``data`` directory. One may
simply want to mark up the existing directory as a dataset.
This can be achieved using the ``dtool markup`` command.

Let's create some dummy data to illustrate this.

.. code-block:: none

    $ mkdir my_existing data
    $ cd my_existing/
    $ ls
    $ touch file1.txt file2.txt

Now one can use the ``dtool markup`` command to annotate the
directory as a dataset.

.. code-block:: none

    $ dtool markup
    project_name [project_name]: world_peace
    dataset_name [dataset_name]: stuff_i_dont_want_to_reorganise
    confidential [False]:
    personally_identifiable_information [False]:
    owner_name [Your Name]: Tjelvar Olsson
    owner_email [olssont@nbi.ac.uk]:
    owner_username [olssont]:
    date [2017-02-24]:
