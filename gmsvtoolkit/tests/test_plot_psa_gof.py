#!/usr/bin/env python
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
import glob
import atexit
import shutil
import tempfile
import unittest

# Import GMSVToolkit modules
import seqnum
from core import gmsvtoolkit_config
from plots import plot_psa_gof
from plots import plot_vs30_gof
from plots import plot_dist_gof
from plots import plot_map_gof
from core.station_list import StationList

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestPlotPSAGoF(unittest.TestCase):
    """
    Unit test for the PSA plot_xxx_gof modules
    """

    def setUp(self):
        """
        Sets up the environment for the test
        """
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        self.labels = ["NR", "10000000"]
        self.max_cutoff = 120
        self.comp_label = "NR-10000000"
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)
            
    def test_plot_psa_gof(self):
        """
        Test the plot_psa_gof module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        plot_title = "GoF Comparison between NR and simulation 10000000"
        
        # Run PSA GoF plotting code
        plot_psa_gof.plot_psa_gof(ref_dir, self.temp_dir,
                                  plot_title, self.comp_label,
                                  max_cutoff=self.max_cutoff)
        
    def test_plot_dist_gof(self):
        """
        Test the plot_dist_gof module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        plot_title = "GoF Comparison between NR and simulation 10000000"
        plot_mode = "rd50"
        
        # Run PSA distance GoF plotting code
        plot_dist_gof.plot_dist_gof(ref_dir, self.temp_dir,
                                    self.comp_label, plot_mode,
                                    plot_title)
        
    def test_plot_vs30_gof(self):
        """
        Test the plot_vs30_gof module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        plot_title = "GoF Comparison between NR and simulation 10000000"
        plot_mode = "rd50"
        
        # Run PSA Vs30 GoF plotting code
        plot_vs30_gof.plot_vs30_gof(ref_dir, self.temp_dir,
                                    self.comp_label, plot_mode,
                                    plot_title)
        
    def test_plot_map_gof(self):
        """
        Test the plot_map_gof module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        plot_title = "GoF Comparison between NR and simulation 10000000"
        r_station_list = "nr_v19_06_2_3_stations.stl"
        r_src_file = "nr-gp-0000.src"
        a_station_list = os.path.join(ref_dir, r_station_list)
        a_src_file = os.path.join(ref_dir, r_src_file)
        plot_mode = "rd50"
        
        # Run the PSA map GoF plotting code
        plot_map_gof.plot_map_gof(ref_dir, self.temp_dir,
                                  self.comp_label, plot_mode,
                                  a_src_file, a_station_list,
                                  plot_title=plot_title)

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPlotPSAGoF)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
