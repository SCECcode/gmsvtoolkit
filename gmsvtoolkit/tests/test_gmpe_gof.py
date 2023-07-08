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
from models import gmpe_config
from core import gmsvtoolkit_config
from stats import gmpe_gof
from core.station_list import StationList
import cmp_bbp

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestGMPEGoF(unittest.TestCase):
    """
    Unit test for the gmpe_gof.py module
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
            
    def test_gmpe_gof(self):
        """
        Test the gmpe_gof module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        obs_dir = os.path.join(ref_dir, "obs")
        gmpe_dir = os.path.join(ref_dir, "gmpe")

        r_station_list = "nr_v19_06_2_3_stations.stl"
        r_src_file = "nr-gp-0000.src"
        a_station_list = os.path.join(ref_dir, r_station_list)
        a_src_file = os.path.join(ref_dir, r_src_file)
        gmpe_group_name = "nga-west2"
        gmpe_group = [item.lower() for item in gmpe_config.GMPES[gmpe_group_name]["models"]]
        comp_label = "NR"

        gmpe_gof_obj = gmpe_gof.GMPEGoF(comp_label=comp_label,
                                        gmpe_group_name=gmpe_group_name)
        gmpe_gof_obj.run_gmpe_gof(a_station_list, a_src_file,
                                  gmpe_dir, obs_dir, self.temp_dir)

        # Check results
        for gmpe in gmpe_group:
            filename = "%s.resid.txt" % (gmpe)
            resid_ref_file = os.path.join(gmpe_dir, filename)
            resid_file = os.path.join(self.temp_dir, filename)
            self.assertFalse(cmp_bbp.cmp_resid(resid_ref_file,
                                               resid_file,
                                               tolerance=0.005) != 0,
                             "output resid file %s does not match reference resid file %s" %
                             (resid_file, resid_ref_file))
        
if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestGMPEGoF)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
