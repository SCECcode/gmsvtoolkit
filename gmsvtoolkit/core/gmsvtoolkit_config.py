#!/usr/bin/env python
"""
BSD 3-Clause License

Copyright (c) 2022, University of Southern California
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

This config class will encapsulate the installation configuration
parameters and several directory paths required by the GMSVToolkit package.
There are no user-changeable parameters in this file.
"""
from __future__ import division, print_function

# Import Python modules
import os
import sys
import time

instance = None

class GMSVToolKitConfig(object):
    """
    Define the configuration parameters that need to be edited when the
    code is moved to a new computer or computer account
    """

    @staticmethod
    def get_instance():
        """
        This function returns an existing instance of
        GMSVToolKitConfig. If one doesn't exit yet, we
        can create one.
        """
        global instance
        if instance is None:
            instance = GMSVToolKitConfig()
        return instance

    def __init__(self):
        """
        This function sets up all relative directories in the
        package. It requires the user to set up GMSVTOOLKIT_DIR.
        """
        #################################################################
        #                                                               #
        #                         Attention!!!                          #
        #      Users shouldn't need to change anything in this file     #
        #                                                               #
        #################################################################

        # First we make sure we have all environment variables that we need
        if "GMSVTOOLKIT_DIR" in os.environ:
            self.GMSVTOOLKIT_ROOT = os.path.normpath(os.environ["GMSVTOOLKIT_DIR"])
        else:
            print("GMSVTOOLKIT_DIR is not set. Please configure it and try again.")
            sys.exit(-1)

        #
        # Make sure these exist before continuing and that you have permissions
        #
        if not os.path.exists(self.GMSVTOOLKIT_ROOT):
            print("Your GMSVToolKit root directory %s doesn't exist." %
                  (self.GMSVTOOLKIT_ROOT))
            print("Please make sure to set GMSVTOOLKIT_DIR correctly to point to")
            print("your GMSVToolkit root directory and try again.")
            sys.exit(-1)
        if not (os.access(self.GMSVTOOLKIT_ROOT, os.R_OK)):
            print("You don't have read access to %s, which is your " %
                  (self.GMSVTOOLKIT_ROOT))
            print("GMSVToolkit root directory. If this is incorrect,")
            print("please set GMSVTOOLKIT_DIR correctly to point to your")
            print("GMSVToolkit root directory and try again.")
            sys.exit(-2)

        #
        # Component installation info
        #
        self.GMSVTOOLKIT_DIR = self.GMSVTOOLKIT_ROOT
        self.TEST_DIR = os.path.join(self.GMSVTOOLKIT_ROOT, "tests")
        self.SRC_DIR = os.path.join(self.GMSVTOOLKIT_ROOT, "src")
        self.PLOT_DATA_DIR = os.path.join(self.GMSVTOOLKIT_ROOT, "plots", "data")

        #
        # Read GMSVToolkit version
        #
        version_file = open(os.path.join(self.GMSVTOOLKIT_DIR, "version.txt"), 'r')
        self.VERSION = version_file.readline().strip()
        version_file.close()

        #
        # Acceptance and Unit Test Directories
        #
        self.TEST_REF_DIR = os.path.join(self.TEST_DIR, "ref_data")

        #
        # GP Directories
        #
        self.GP_BIN_DIR = os.path.join(self.SRC_DIR, "gp", "bin")
        if not os.path.exists(self.GP_BIN_DIR):
            print("Can't find GP bin directory %s." % (self.GP_BIN_DIR))
            print("Did you successfully build the executables?")
            print("If not, please run make in %s." % (self.SRC_DIR))
            sys.exit(3)

        #
        # UCB Directories
        #
        self.UCB_BIN_DIR = os.path.join(self.SRC_DIR, "ucb", "rotd50")
        if not os.path.exists(self.UCB_BIN_DIR):
            print("Can't find UCB bin directory %s." % (self.UCB_BIN_DIR))
            print("Did you successfully build the executables?")
            print("If not, please run make in %s." % (self.SRC_DIR))
            sys.exit(3)

        #
        # USGS Directories
        #
        self.USGS_BIN_DIR = os.path.join(self.SRC_DIR, "usgs", "bin")
        if not os.path.exists(self.USGS_BIN_DIR):
            print("Can't find USGS bin directory %s." %
                  (self.USGS_BIN_DIR))
            print("Did you successfully build the executables?")
            print("If not, please run make in %s." % (self.SRC_DIR))
            sys.exit(3)
