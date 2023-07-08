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

Unit tests for the peer_formatter tools
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import atexit
import shutil
import tempfile
import unittest

# Import GMSVTOOLKIT modules
import seqnum
from core import gmsvtoolkit_config
from utils.peer_formatter import bbp2peer, peer2bbp

def cleanup(dir_name):
    """
    This function removes the temporary directory
    """
    shutil.rmtree(dir_name)

class TestPEERFormat(unittest.TestCase):
    """
    Unit tests for the peer_formatter module
    """

    def setUp(self):
        """
        Configures the environment for the tests
        """
        self.install = gmsvtoolkit_config.GMSVToolKitConfig.get_instance()
        
        if "GMSVTOOLKIT_TESTDIR" in os.environ:
            self.temp_dir = os.path.join(os.environ["GMSVTOOLKIT_TESTDIR"],
                                         str(int(seqnum.get_seq_num())))
        else:
            self.temp_dir = tempfile.mkdtemp()
            # Add clean up for later
            atexit.register(cleanup, self.temp_dir)

    def test_bbp2peer(self):
        """
        Test for the bbp2peer converter
        """
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "utils")
        in_bbp_file = os.path.join(ref_dir, "station.acc.bbp")
        peer_n_out = os.path.join(self.temp_dir, "output_peer_n.acc")
        peer_e_out = os.path.join(self.temp_dir, "output_peer_e.acc")
        peer_z_out = os.path.join(self.temp_dir, "output_peer_z.acc")
        for out_file in [peer_n_out, peer_e_out, peer_z_out]:
            try:
                os.remove(out_file)
            except:
                pass

        #
        # Simplest reference filename
        #
        peer_n_out_ref = os.path.join(ref_dir, "station.peer_n.acc")
        peer_e_out_ref = os.path.join(ref_dir, "station.peer_e.acc")
        peer_z_out_ref = os.path.join(ref_dir, "station.peer_z.acc")

        bbp2peer(in_bbp_file, peer_n_out, peer_e_out, peer_z_out)
        #print("created PEER-format files: %s %s %s" %
        #      (peer_n_out, peer_e_out, peer_z_out))

        res_file = open(peer_n_out, 'r')
        res_lines = 0
        for line in res_file:
            res_lines = res_lines + 1
        res_file.close()

        ref_file = open(peer_n_out_ref, 'r')
        ref_lines = 0
        for line in ref_file:
            ref_lines = ref_lines + 1
        ref_file.close()
        #
        # Check files have same number of lines
        #
        self.assertTrue(res_lines == ref_lines)

    def test_peer2bbp(self):
        """
        Test for the peer2bbp converter
        """
        ref_dir = os.path.join(self.install.TEST_REF_DIR, "utils")
        # Retrieve PEER seismogram files
        in_n_file = os.path.join(ref_dir, "station.peer_n.acc")
        in_e_file = os.path.join(ref_dir, "station.peer_e.acc")
        in_z_file = os.path.join(ref_dir, "station.peer_z.acc")

        # Output file
        out_bbp_file = os.path.join(self.temp_dir, "station.output.bbp")
        try:
            os.remove(out_bbp_file)
        except:
            pass
        
        # Reference bbp filename
        out_bbp_ref = os.path.join(ref_dir, "station.acc.bbp")

        peer2bbp(in_n_file, in_e_file, in_z_file, out_bbp_file)
        #print("created bbp file: %s" % (out_bbp_file))

        res_file = open(out_bbp_file, 'r')
        res_lines = 0
        for line in res_file:
            res_lines = res_lines + 1
        res_file.close()

        ref_file = open(out_bbp_ref, 'r')
        ref_lines = 0
        for line in ref_file:
            ref_lines = ref_lines + 1
        ref_file.close()
        #
        # Check files have the same number of lines
        #
        self.assertTrue(res_lines == ref_lines)

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(TestPEERFormat)
    RETURN_CODE = unittest.TextTestRunner(verbosity=2).run(SUITE)
    sys.exit(not RETURN_CODE.wasSuccessful())
