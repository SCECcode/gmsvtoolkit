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
from plots import plot_fas

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestPlotFAS(unittest.TestCase):
    """
    Unit test for the FAS plot_fas module
    """

    def setUp(self):
        """
        Sets up the environment for the test
        """
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        self.station_id = "2001-SCE"
        self.station_list = "nr_v19_06_2_3_stations.stl"
        self.batch_list = "nr_v19_06_2_3_stations.txt"
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)
            
    def test_plot_fas(self):
        """
        Test the plot_fas module with single plot
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        input_file = os.path.join(ref_dir, "10000000.2001-SCE.smc8.smooth.fs.col")
        output_file = os.path.join(self.temp_dir, "2001-SCE.fas.png")
        
        # Run FAS plotting code
        plot_fas.run_single_station(input_file, output_file,
                                    self.station_id)
        
    def test_plot_fas_batch(self):
        """
        Test the plot_fas module with batch mode
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        batch_file = os.path.join(ref_dir, self.batch_list)
        
        # Run FAS plotting code in batch mode
        plot_fas.run_batch_mode(batch_file, ref_dir,
                                self.temp_dir)
        
    def test_plot_fas_station(self):
        """
        Test the plot_fas module with station list
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        station_list = os.path.join(ref_dir, self.station_list)
        
        # Run FAS plotting code in station list mode
        plot_fas.run_station_mode(station_list, ref_dir,
                                  self.temp_dir)

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPlotFAS)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
