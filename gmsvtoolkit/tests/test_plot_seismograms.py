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
from plots import plot_seismograms

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestPlotSeismograms(unittest.TestCase):
    """
    Unit test for the plot_seismograms module
    """

    def setUp(self):
        """
        Sets up the environment for the test
        """
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        self.comp_label = "10000000."
        self.comp_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)
            
    def test_plot_seismograms_single(self):
        """
        Test the plot_seismograms module single station mode
        """
        # Input parameters
        station_name = "2001-SCE"
        # Use data from two different stations, just for testing the
        # plotting code, would use different sets for same station
        # in real life
        input_files = ["10000000.2001-SCE.acc.bbp",
                       "10000000.2002-SYL.acc.bbp"]
        input_files = [os.path.join(self.comp_dir,
                                    input_file) for input_file in input_files]
        xmin = 0.0
        xmax = 40.0
        mode = ["vel", "acc", "dis"]
        labels = None
        output_file = "%s%s_seis.png" % (self.comp_label,
                                         station_name)
        output_file = os.path.join(self.temp_dir, output_file)

        # Run plot seismograms code, test both 2-, and 3-component plotting
        plot_seismograms_obj = plot_seismograms.PlotSeismograms(mode=mode,
                                                                n_comp=2)
        plot_seismograms_obj.run_single_station(input_files, labels,
                                                output_file, station_name,
                                                xmin, xmax, plot_title=None)
        plot_seismograms_obj = plot_seismograms.PlotSeismograms(mode=mode,
                                                                n_comp=3)
        plot_seismograms_obj.run_single_station(input_files, labels,
                                                output_file, station_name,
                                                xmin, xmax, plot_title=None)
        
    def test_plot_seismograms_station_list(self):
        """
        Test the plot_seismograms module with a station list
        """
        station_file = os.path.join(self.comp_dir, "nr_v19_06_2_2_stations.stl")
        xmin = 0.0
        xmax = 40.0
        mode = ["vel", "acc", "dis"]
        n_comp = 3
        labels = None

        # Run plot seismograms code
        plot_seismograms_obj = plot_seismograms.PlotSeismograms(mode=mode,
                                                                n_comp=n_comp)
        plot_seismograms_obj.run_station_mode(station_file, [self.comp_dir],
                                              labels, self.temp_dir,
                                              self.comp_label, xmin, xmax,
                                              plot_title=None)

    def test_plot_seismograms_batch(self):
        """
        Test the plot_seismograms module in batch mode
        """
        batch_file = os.path.join(self.comp_dir, "nr_v19_06_2_2_stations.txt")
        xmin = 0.0
        xmax = 40.0
        mode = ["vel", "acc", "dis"]
        n_comp = 3
        labels = None
        
        # Run plot seismograms code
        plot_seismograms_obj = plot_seismograms.PlotSeismograms(mode=mode,
                                                                n_comp=n_comp)
        plot_seismograms_obj.run_batch_mode(batch_file, [self.comp_dir],
                                            labels, self.temp_dir,
                                            self.comp_label, xmin, xmax,
                                            plot_title=None)

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPlotSeismograms)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
