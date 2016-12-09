#!/bin/bash

# Clean up old stuff
rm -f deploy/docker/*.whl
rm -f dist/*

# Build and copy wheel
python3 setup.py bdist_wheel
cp dist/*.whl deploy/docker/dtool-0.2.0-py3-none-any.whl

# Build docker image
docker build -t jicscicomp/dtool deploy/docker/

# Build singularity image
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/mnt/cluster_home/singularity/:/output \
    --privileged \
    -t \
    --rm \
    mcdocker2singularity \
    jicscicomp/dtool \
    arctool \

