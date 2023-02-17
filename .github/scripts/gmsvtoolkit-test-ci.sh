#!/bin/bash

# Set basic parameters
BASEDIR="${RUNNER_WORKSPACE}"
GMSVTOOLKIT_DIR="${BASEDIR}/gmsvtoolkit/gmsvtoolkit"
SRCDIR="${GMSVTOOLKIT_DIR}/src"

export GMSVTOOLKIT_DIR=${GMSVTOOLKIT_DIR}
export PYTHONPATH=${GMSVTOOLKIT_DIR}:${PYTHONPATH}

echo
echo "===> Running Unit Tests..."

cd $GMSVTOOLKIT_DIR/tests
./UnitTests.py
