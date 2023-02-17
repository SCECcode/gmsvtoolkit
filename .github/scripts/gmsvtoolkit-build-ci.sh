#!/bin/bash

echo

OLD_DIR=`pwd`
mkdir ${RUNNER_WORKSPACE}/bin
cd ${RUNNER_WORKSPACE}/bin
ln -s /usr/bin/gcc-8 gcc
ln -s /usr/bin/gfortran-8 gfortran
cd ${OLD_DIR}
export PATH=${RUNNER_WORKSPACE}/bin:$PATH

echo "======================GCC===================="
gcc --version

echo "===================GFORTRAN=================="
gfortran --version

echo "===================Python 3=================="
python3 --version
python3 -c "import numpy; print('Numpy: ', numpy.__version__)"
python3 -c "import scipy; print('SciPy: ', scipy.__version__)"
python3 -c "import matplotlib; print('Matplotlib: ', matplotlib.__version__)"

# Set basic parameters
BASEDIR="${RUNNER_WORKSPACE}"
GMSVTOOLKIT_DIR="${BASEDIR}/gmsvtoolkit/gmsvtoolkit"
SRCDIR="${GMSVTOOLKIT_DIR}/src"

# Compile source distribution
echo "=> Main GMSVToolkit Source Distribution"
echo "==> Compiling... (it may take a while)"
OLD_DIR=`pwd`
cd ${SRCDIR}
make
cd ${OLD_DIR}
# Done with main source distribution
echo "==> Source code compiled!"
echo

echo "==> Build steps completed!"
