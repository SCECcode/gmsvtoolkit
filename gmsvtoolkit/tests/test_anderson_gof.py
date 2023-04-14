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
import cmp_bbp
import seqnum
from core import gmsvtoolkit_config
from stats import anderson_gof
from core.station_list import StationList

#import bband_utils

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestAndersonGoF(unittest.TestCase):
    """
    Unit test for anderson_gof.py
    """

    def setUp(self):
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)
        
    def test_anderson_gof(self):
        """
        Run the Anderson GOF test
        """
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "stats")
        obs_dir = os.path.join(self.install.TEST_REF_DIR, "obs")
        comp_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        
        station_file = os.path.join(ref_dir, "nr_v19_06_2_3_stations.stl")
        event_name = "NR"

        # Run Anderson GoF module
        gof_obj = anderson_gof.AndersonGOF(station_file=station_file,
                                           event_name=event_name)
        gof_obj.run_anderson_gof(obs_dir, comp_dir, self.temp_dir)

        # Check summary GOF file
        ref_sum_file = os.path.join(ref_dir, "anderson_gof",
                                    "gof_anderson.%s.txt" % (event_name))
        cal_sum_file = os.path.join(self.temp_dir, "gof_anderson.%s.txt" %
                                    (event_name))
        self.assertFalse(cmp_bbp.cmp_files_generic(ref_sum_file, cal_sum_file,
                                                   tolerance=0.005,
                                                   start_col=1) != 0,
                         "GOF Summary file does not match reference file!")

        # Read station list
        station_list = StationList(station_file)
        stations = station_list.get_station_list()

        # Loop over stations
        for site in stations:
            station_name = site.scode

            # Check per-station files
            ref_sum_file = os.path.join(ref_dir, "anderson_gof",
                                        "gof-%s-anderson-%s.txt" %
                                        (event_name, station_name))
            cal_sum_file = os.path.join(self.temp_dir,
                                        "gof-%s-anderson-%s.txt" %
                                        (event_name, station_name))
            self.assertFalse(cmp_bbp.cmp_files_generic(ref_sum_file, cal_sum_file,
                                                       tolerance=0.005,
                                                       start_col=1) != 0,
                             "GOF file for station %s does not match!" %
                             (station_name))

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestAndersonGoF)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
