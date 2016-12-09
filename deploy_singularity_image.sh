#!/bin/bash

# Clean up old stuff
rm -f deploy/docker/*.whl
rm -f dist/*

# Build and copy wheel
python3 setup.py bdist_wheel
cp dist/*.whl deploy/docker/dtool-0.2.0-py3-none-any.whl

# Build docker image
docker build -t jicscicomp/dtool deploy/docker/

