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
from core.timeseries import Timeseries
import cmp_bbp

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestTimeseries(unittest.TestCase):
    """
    Unit test for GMSV Toolkit's Timeseries module
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

    def test_timeseries_differentiate(self):
        """
        Test timeseries differentiation
        """
        # Reference directory
        input_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "timeseries")

        vel_file = "10000000.2001-SCE.vel.bbp"
        acc_file = "2001-SCE.acc.bbp"
        a_vel_file = os.path.join(input_dir, vel_file)
        a_acc_file = os.path.join(self.temp_dir, acc_file)
        ref_file = os.path.join(ref_dir, acc_file)

        station_data = Timeseries(input_file=a_vel_file, station_name="2001-SCE")
        station_data.convert_to_acc()
        station_data.write_bbp(a_acc_file)

        self.assertFalse(cmp_bbp.cmp_bbp(ref_file,
                                         a_acc_file) != 0,
                         "Output file %s does not match reference file: %s" %
                         (acc_file, ref_file))

    def test_timeseries_integrate(self):
        """
        Test timeseries integration
        """
        # Reference directory
        input_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "timeseries")

        vel_file = "10000000.2001-SCE.vel.bbp"
        dis_file = "2001-SCE.dis.bbp"
        a_vel_file = os.path.join(input_dir, vel_file)
        a_dis_file = os.path.join(self.temp_dir, dis_file)
        ref_file = os.path.join(ref_dir, dis_file)

        station_data = Timeseries(input_file=a_vel_file, station_name="2001-SCE")
        station_data.convert_to_dis()
        station_data.write_bbp(a_dis_file)

        self.assertFalse(cmp_bbp.cmp_bbp(ref_file,
                                         a_dis_file) != 0,
                         "Output file %s does not match reference file: %s" %
                         (dis_file, ref_file))

    def test_timeseries_rotate(self):
        """
        Test timeseries rotation
        """
        # Reference directory
        input_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "timeseries")

        vel_file = "10000000.2001-SCE.vel.bbp"
        rot_file = "2001-SCE.rot.vel.bbp"
        a_vel_file = os.path.join(input_dir, vel_file)
        a_rot_file = os.path.join(self.temp_dir, rot_file)
        ref_file = os.path.join(ref_dir, rot_file)

        station_data = Timeseries(input_file=a_vel_file, station_name="2001-SCE")
        station_data.rotate(30)
        station_data.write_bbp(a_rot_file)

        self.assertFalse(cmp_bbp.cmp_bbp(ref_file,
                                         a_rot_file) != 0,
                         "Output file %s does not match reference file: %s" %
                         (rot_file, ref_file))

    def test_timeseries_interpolate(self):
        """
        Test timeseries interpolation
        """
        # Reference directory
        input_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "timeseries")

        vel_file = "10000000.2001-SCE.vel.bbp"
        interp_file = "2001-SCE.002.vel.bbp"
        a_vel_file = os.path.join(input_dir, vel_file)
        a_interp_file = os.path.join(self.temp_dir, interp_file)
        ref_file = os.path.join(ref_dir, interp_file)

        station_data = Timeseries(input_file=a_vel_file, station_name="2001-SCE")
        station_data.interp(0.02)
        station_data.write_bbp(a_interp_file)

        self.assertFalse(cmp_bbp.cmp_bbp(ref_file,
                                         a_interp_file) != 0,
                         "Output file %s does not match reference file: %s" %
                         (interp_file, ref_file))

    def test_timeseries_plot(self):
        """
        Test timeseries plotting function
        """
        # Reference directory
        input_dir = os.path.join(self.install.TEST_REF_DIR, "metrics")

        vel_file = "10000000.2001-SCE.vel.bbp"
        a_vel_file = os.path.join(input_dir, vel_file)
        output_plot = os.path.join(self.temp_dir, "10000000.2001-SCE.vel.png")

        station_data = Timeseries(input_file=a_vel_file, station_name="2001-SCE")
        station_data.plot(output_plot)

if __name__ == "__main__":
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestTimeseries)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
