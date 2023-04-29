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
from utils import gmsv_tools
from core.station_list import StationList
import cmp_bbp

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestGMSVTools(unittest.TestCase):
    """
    Unit test for the gmsv_tools.py module
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

    def test_gmsvtools_differentiate(self):
        """
        Test the gmsv_tools differentiation code
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        vel_file = "10000000.2001-SCE.vel.bbp"
        a_vel_file = os.path.join(ref_dir, vel_file)

        gmsv_tools.convert_file(a_vel_file, "vel", "acc",
                                output_dir=self.temp_dir,
                                temp_dir=self.temp_dir)

    def test_gmsvtools_integrate(self):
        """
        Test the gmsv_tools integreation code
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        vel_file = "10000000.2001-SCE.vel.bbp"
        a_vel_file = os.path.join(ref_dir, vel_file)

        gmsv_tools.convert_file(a_vel_file, "vel", "dis",
                                output_dir=self.temp_dir,
                                temp_dir=self.temp_dir)

    def test_gmsvtools_station(self):
        """
        Test the gmsv_tools in station mode
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        r_station_list = "nr_v19_06_2_2_stations.stl"
        a_station_list = os.path.join(ref_dir, r_station_list)

        # Run gmsv_tools
        gmsv_tools.convert_station_file(a_station_list, "acc",
                                        "dis", ref_dir, self.temp_dir,
                                        temp_dir=self.temp_dir)

        # Check results
        stations = StationList(a_station_list)
        station_list = stations.get_station_list()

        # Loop through stations
        for station in station_list:
            station_name = station.scode

            # Find input reference file
            input_list = glob.glob("%s%s*%s*.dis.bbp" %
                                   (ref_dir, os.sep, station_name))
            if len(input_list) != 1:
                print("[ERROR]: Can't find reference file for station %s" % (station_name))
                sys.exit(1)
            ref_file = input_list[0]

            # Find input calculated file
            input_list = glob.glob("%s%s*%s*.dis.bbp" %
                                   (self.temp_dir, os.sep, station_name))
            if len(input_list) != 1:
                print("[ERROR]: Can't find calculated file for station %s" % (station_name))
                sys.exit(1)
            comp_file = input_list[0]

            self.assertFalse(cmp_bbp.cmp_bbp(ref_file,
                                             comp_file) != 0,
                             "Output file %s does not match reference file: %s" %
                             (comp_file, ref_file))

    def test_gmsvtools_batch(self):
        """
        Test the gmsv_tools in batch mode
        """
        # Reference directory
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        r_batch_file = "nr_v19_06_2_2_stations.txt"
        a_batch_file = os.path.join(ref_dir, r_batch_file)

        # Run gmsv_tools
        gmsv_tools.convert_batch_file(a_batch_file, "acc",
                                      "dis", ref_dir, self.temp_dir,
                                      temp_dir=self.temp_dir)

        # Loop through stations
        input_file = open(a_batch_file, 'r')
        for line in input_file:
            line = line.strip()
            if not line:
                continue

            station_name = line

            # Find input reference file
            input_list = glob.glob("%s%s*%s*.dis.bbp" %
                                   (ref_dir, os.sep, station_name))
            if len(input_list) != 1:
                print("[ERROR]: Can't find reference file for station %s" % (station_name))
                sys.exit(1)
            ref_file = input_list[0]

            # Find input calculated file
            input_list = glob.glob("%s%s*%s*.dis.bbp" %
                                   (self.temp_dir, os.sep, station_name))
            if len(input_list) != 1:
                print("[ERROR]: Can't find calculated file for station %s" % (station_name))
                sys.exit(1)
            comp_file = input_list[0]

            self.assertFalse(cmp_bbp.cmp_bbp(ref_file,
                                             comp_file) != 0,
                             "Output file %s does not match reference file: %s" %
                             (comp_file, ref_file))
        input_file.close()

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestGMSVTools)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
