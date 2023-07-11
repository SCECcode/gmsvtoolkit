#! /usr/bin/env python3
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
import atexit
import shutil
import tempfile
import unittest

# Import Broadband modules
import cmp_bbp
import seqnum
from core import gmsvtoolkit_config
from metrics.rzz2015 import RZZ2015

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestRZZ2015(unittest.TestCase):
    """
    Unit test for rzz2015.py
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

    def test_rzz2015(self):
        """
        Run the RZZ2015 test
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        sim_dir = ref_dir
        obs_dir = os.path.join(self.install.TEST_REF_DIR, "obs")
        label = "NR"
        output_file = os.path.join(self.temp_dir, "rzz2015.%s.txt" % (label))
        ref_file = os.path.join(ref_dir, "rzz2015_NR_3_stations.txt")

        a_station_list = os.path.join(ref_dir, "nr_v19_06_2_3_stations.stl")

        rzz_obj = RZZ2015()
        rzz_obj.run_rzz2015(a_station_list, label,
                            sim_dir, obs_dir,
                            output_file)

        # Check results
        self.assertFalse(cmp_bbp.cmp_files_generic(ref_file, output_file,
                                                   tolerance=1.0,
                                                   start_col=1,
                                                   sep=",") != 0,
                         "RZZ2015 Summary file does not match reference file!")

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRZZ2015)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
