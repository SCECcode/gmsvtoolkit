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
import glob
import atexit
import shutil
import tempfile
import unittest

# Import GMSVToolkit modules
import seqnum
from core import gmsvtoolkit_config
from metrics import rotdxx
from core.station_list import StationList
import cmp_bbp

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestRotDXX(unittest.TestCase):
    """
    Unit test for the rotdxx.py module
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
            
    def test_rotdxx(self):
        """
        Test the rotdxx module
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        r_station_list = "nr_v19_06_2_3_stations.stl"
        a_station_list = os.path.join(ref_dir, r_station_list)

        rotdxx_obj = rotdxx.RotDXX(mode="both")
        rotdxx_obj.run_station_mode(a_station_list, ref_dir,
                                    self.temp_dir, temp_dir=self.temp_dir)

        # Check results
        stations = StationList(a_station_list)
        station_list = stations.get_station_list()

        # Loop through stations
        for station in station_list:
            station_name = station.scode

            for ext in [".rd50", ".rd100"]:
            
                # Find input reference file
                input_list = glob.glob("%s%s*%s*%s" %
                                       (ref_dir, os.sep, station_name, ext))
                if len(input_list) != 1:
                    print("[ERROR]: Can't find reference file for station %s" % (station_name))
                    sys.exit(1)
                ref_file = input_list[0]

                # Find input calculated file
                input_list = glob.glob("%s%s*%s*%s" %
                                       (self.temp_dir, os.sep, station_name, ext))
                if len(input_list) != 1:
                    print("[ERROR]: Can't find calculated file for station %s" % (station_name))
                    sys.exit(1)
                comp_file = input_list[0]
            
                self.assertFalse(cmp_bbp.cmp_files_generic(ref_file,
                                                           comp_file) != 0,
                                 "Output file %s does not match reference file: %s" %
                                 (comp_file, ref_file))

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRotDXX)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
