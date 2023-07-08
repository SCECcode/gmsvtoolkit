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
from plots import plot_gmpe
from models import gmpe_config

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestPlotGMPE(unittest.TestCase):
    """
    Unit test for the plot_gmpe module
    """

    def setUp(self):
        """
        Sets up the environment for the test
        """
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        self.gmpe_group_name = "nga-west2"
        self.comp_label = "NR"
        self.gmpe_dir = os.path.join(self.install.TEST_REF_DIR, "stats", "gmpe")
        self.comp_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        gmpe_group = gmpe_config.GMPES[self.gmpe_group_name]
        self.gmpe_labels = gmpe_group["labels"]
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)
            
    def test_plot_gmpe_single(self):
        """
        Test the plot_gmpe module single station mode
        """
        # Reference directory
        station_name = "2001-SCE"
        output_file = "%s_%s_gmpe.png" % (self.comp_label,
                                          station_name)
        output_file = os.path.join(self.temp_dir, output_file)
        
        # Run PSA GoF plotting code
        plot_gmpe.run_single_station(station_name, self.gmpe_dir,
                                     self.comp_dir, output_file,
                                     self.gmpe_labels)
                
    def test_plot_gmpe_station_list(self):
        """
        Test the plot_gmpe module with a station list
        """
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        station_file = os.path.join(ref_dir, "nr_v19_06_2_3_stations.stl")
        run_prefix = "123456"
        
        # Run PSA distance GoF plotting code
        plot_gmpe.run_station_mode(station_file, self.gmpe_dir,
                                   self.comp_dir, self.temp_dir,
                                   self.gmpe_labels,
                                   comp_label=self.comp_label,
                                   run_prefix=run_prefix)
        
    def test_plot_gmpe_batch(self):
        """
        Test the plot_gmpe module in batch mode
        """
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        batch_file = os.path.join(ref_dir, "nr_v19_06_2_3_stations.txt")
        run_prefix = "123456"
        
        # Run PSA Vs30 GoF plotting code
        plot_gmpe.run_batch_mode(batch_file, self.gmpe_dir,
                                 self.comp_dir, self.temp_dir,
                                 self.gmpe_labels,
                                 comp_label=self.comp_label,
                                 run_prefix=run_prefix)
                
if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPlotGMPE)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
