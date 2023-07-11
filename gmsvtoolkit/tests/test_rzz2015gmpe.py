#!/usr/bin/env python3
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
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import math
import atexit
import shutil
import tempfile
import unittest

# Import GMSV Toolkit modules
import cmp_bbp
import seqnum
from core import gmsvtoolkit_config
from models.rzz2015_gmpe import RZZ2015GMPE

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

def compare_values(val1, val2, tolerance=0.01):
    """
    Check if two values are within a given tolerance,
    return True if yes, or False if no.
    """
    return math.fabs((val1 - val2) / val1) <= tolerance

class TestRZZ2015GMPE(unittest.TestCase):
    """
    Unit test for rzz2015_gmpe.py
    """

    def setUp(self):
        """
        Sets up the environment for the test
        """
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)

        self.stations = "nr_v19_06_2.stl"
        self.source = "nr_v14_02_1.src"

    def test_rzz2015_gmpe(self):
        """
        Run the RZZ2015 GMPE test
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        a_station_list = os.path.join(ref_dir, "nr_v19_06_2_3_stations.stl")
        a_src_file = os.path.join(ref_dir, "nr-gp-0000.src")
        a_output_file = os.path.join(self.temp_dir, "rzz2015_gmpe_calc.txt")
        a_ref_file = os.path.join(self.install.TEST_REF_DIR, "models",
                                  "rzz2015_gmpe_3_stations_ref.txt")

        rzz2015_gmpe_obj = RZZ2015GMPE()
        rzz2015_gmpe_obj.run_rzz2015_gmpe(a_station_list, a_src_file,
                                          a_output_file)

        # Check results
        self.assertFalse(cmp_bbp.cmp_files_generic(a_ref_file, a_output_file,
                                                   tolerance=0.005,
                                                   start_col=1,
                                                   sep=",") != 0,
                         "RZZ2015 GMPE results don't match reference file!")

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRZZ2015GMPE)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
