Developer notes
===============

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
