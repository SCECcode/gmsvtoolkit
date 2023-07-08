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
import atexit
import shutil
import tempfile
import unittest

# Import GMSVToolkit modules
import seqnum
from core import gmsvtoolkit_config
from stats import psa_gof
from core.station_list import StationList
import cmp_bbp

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestPSAGoF(unittest.TestCase):
    """
    Unit test for the psa_gof.py module
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
            
    def test_psa_gof(self):
        """
        Test the psa_gof module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        obs_dir = os.path.join(ref_dir, "obs")
        sims_dir = os.path.join(ref_dir, "sims")

        r_station_list = "nr_v19_06_2_3_stations.stl"
        r_src_file = "nr-gp-0000.src"
        a_station_list = os.path.join(ref_dir, r_station_list)
        a_src_file = os.path.join(ref_dir, r_src_file)
        max_cutoff = 120
        comp_label = "NR-10000000"

        psa_gof_obj = psa_gof.PSAGoF(mode="rotd50", max_cutoff=max_cutoff,
                                     comp_label=comp_label)
        psa_gof_obj.run_psa_gof(a_station_list, a_src_file,
                                obs_dir, sims_dir, self.temp_dir)

        # Check results
        resid_ref_file = os.path.join(ref_dir, "NR-10000000.rd50-resid.txt")
        resid_file = os.path.join(self.temp_dir, "NR-10000000.rd50-resid.txt")
        self.assertFalse(cmp_bbp.cmp_resid(resid_ref_file,
                                           resid_file,
                                           tolerance=0.005) != 0,
                         "output resid file %s does not match reference resid file %s" %
                         (resid_file, resid_ref_file))
        
if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPSAGoF)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
