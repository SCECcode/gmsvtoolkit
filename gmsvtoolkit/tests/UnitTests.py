#! /usr/bin/env python
"""
BSD 3-Clause License

Copyright (c) 2023, University of Southern California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Top level test suites for BB Platform
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import atexit
import shutil
import tempfile
import unittest

import seqnum

# Import GMSVToolkit unit test modules
from test_pynga import TestPyNGA
from test_rotdxx import TestRotDXX
from test_plot_rotdxx import TestPlotRotDXX
from test_psa_gof import TestPSAGoF
from test_plot_psa_gof import TestPlotPSAGoF
from test_plot_fas_gof import TestPlotFASGoF
from test_plot_map import TestPlotMap
from test_peer_formatter import TestPEERFormat
from test_plot_fas import TestPlotFAS
from test_plot_fas_comparison import TestPlotFASComparison
from test_fas import TestFAS
from test_fas_gof import TestFASGoF
from test_calc_gmpe import TestCalcGMPE
from test_gmpe_gof import TestGMPEGoF
from test_plot_gmpe_gof import TestPlotGMPEGoF
from test_plot_gmpe import TestPlotGMPE

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class Logger(object):
    def __init__(self, filename):
        self.filename = filename
        self.out_fp = open(self.filename, 'w')

    def write(self, string):
        self.out_fp.write(string)

    def flush(self):
        self.out_fp.flush()

    def close(self):
        self.out_fp.flush()
        self.out_fp.close()

# Initialize
if "GMSVTOOLKIT_TESTDIR" in os.environ:
    LOG_DIR = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                           str(int(seqnum.get_seq_num())))
else:
    # Use current directory
    LOG_DIR = tempfile.mkdtemp()
    # Add clean up for later
    atexit.register(cleanup, LOG_DIR)

sys.stdout = Logger(os.path.join(LOG_DIR, "unit_tests.log"))
TS = unittest.TestSuite()

# Add GMSVToolkit tests
TS.addTest(unittest.makeSuite(TestPyNGA))
TS.addTest(unittest.makeSuite(TestPEERFormat))
TS.addTest(unittest.makeSuite(TestRotDXX))
TS.addTest(unittest.makeSuite(TestPlotRotDXX))
TS.addTest(unittest.makeSuite(TestPSAGoF))
TS.addTest(unittest.makeSuite(TestPlotPSAGoF))
TS.addTest(unittest.makeSuite(TestPlotMap))
TS.addTest(unittest.makeSuite(TestPlotFAS))
TS.addTest(unittest.makeSuite(TestPlotFASComparison))
TS.addTest(unittest.makeSuite(TestFAS))
TS.addTest(unittest.makeSuite(TestFASGoF))
TS.addTest(unittest.makeSuite(TestPlotFASGoF))
TS.addTest(unittest.makeSuite(TestCalcGMPE))
TS.addTest(unittest.makeSuite(TestPlotGMPE))
TS.addTest(unittest.makeSuite(TestGMPEGoF))
TS.addTest(unittest.makeSuite(TestPlotGMPEGoF))

# Done, run the tests
print("==> Running GMSVToolkit Unit Tests...")
RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(TS)
sys.exit(not RETURN_CODE.wasSuccessful())
